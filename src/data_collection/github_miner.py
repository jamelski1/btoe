"""Mine issue-PR pairs from GitHub repositories.

This module handles:
1. Validating target repositories against inclusion criteria
2. Extracting closed issues with linked/merged PRs
3. Computing ground-truth durations (assignment -> merge)
4. Filtering and cleaning the dataset
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd
from github import Github, RateLimitExceededException

from src.utils.config import get_github_token, load_config

logger = logging.getLogger(__name__)


@dataclass
class IssuePRPair:
    """A linked issue-PR pair with metadata."""

    repo: str
    issue_number: int
    issue_title: str
    issue_body: str
    issue_labels: list[str]
    issue_created_at: datetime
    issue_assigned_at: datetime | None
    pr_number: int
    pr_title: str
    pr_body: str
    pr_merged_at: datetime | None
    pr_files_changed: list[str] = field(default_factory=list)
    duration_hours: float | None = None


class GitHubMiner:
    """Mines issue-PR pairs from GitHub repositories."""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.gh = Github(get_github_token(), per_page=100)
        self.filter_cfg = self.config["filtering"]

    def validate_repository(self, owner: str, name: str) -> dict:
        """Check if a repository meets inclusion criteria.

        Returns dict with validation results and repo stats.
        """
        repo = self.gh.get_repo(f"{owner}/{name}")

        # Count closed issues (use search API for accurate totalCount)
        closed_issues = self.gh.search_issues(f"repo:{owner}/{name} is:issue is:closed")
        total_closed = closed_issues.totalCount

        # Check contributor count
        contributors = list(repo.get_contributors()[:self.filter_cfg["min_contributors"] + 1])
        contributor_count = len(contributors)

        # Check repository age
        created = repo.created_at
        age_years = (datetime.now(tz=created.tzinfo) - created).days / 365.25

        # Check license
        license_info = repo.license

        results = {
            "repo": f"{owner}/{name}",
            "total_closed_issues": total_closed,
            "contributor_count": contributor_count,
            "age_years": round(age_years, 1),
            "license": license_info.spdx_id if license_info else "None",
            "meets_issue_threshold": total_closed >= self.filter_cfg["min_closed_issues_with_prs"],
            "meets_contributor_threshold": contributor_count >= self.filter_cfg["min_contributors"],
            "meets_age_threshold": age_years >= self.filter_cfg["min_years_active"],
        }
        results["passes_all"] = all([
            results["meets_issue_threshold"],
            results["meets_contributor_threshold"],
            results["meets_age_threshold"],
        ])

        logger.info(f"Repository validation for {owner}/{name}: {results}")
        return results

    def _handle_rate_limit(self):
        """Wait for GitHub API rate limit reset (core or search)."""
        rate_limit = self.gh.get_rate_limit()
        # Use whichever limit is actually exhausted
        if rate_limit.search.remaining == 0:
            reset_time = rate_limit.search.reset
        else:
            reset_time = rate_limit.core.reset
        wait_seconds = (reset_time - datetime.utcnow()).total_seconds() + 10
        if wait_seconds > 0:
            logger.warning(f"Rate limit hit. Waiting {wait_seconds:.0f}s until reset.")
            time.sleep(wait_seconds)

    def mine_issue_pr_pairs(self, owner: str, name: str, max_pairs: int = None,
                            save_path=None, skip_issue_numbers: set = None,
                            checked_log_path=None) -> list[IssuePRPair]:
        """Mine linked issue-PR pairs from a repository.

        Identifies issues that reference merged PRs through:
        1. PR body references ("fixes #123", "closes #123")
        2. GitHub timeline events (cross-references)
        3. Commit message references

        Args:
            skip_issue_numbers: Set of issue numbers to skip (already collected
                or already evaluated and rejected). The miner adds every issue
                it processes to this set during the run.
            checked_log_path: Path to JSON file storing checked issue numbers.
                Loaded at start, updated periodically, saved at end.
        """
        from pathlib import Path
        import json as _json

        max_pairs = max_pairs or self.filter_cfg["target_sample_size"]
        skip_issue_numbers = set(skip_issue_numbers) if skip_issue_numbers else set()

        # Load persistent checked log (issues we've evaluated before, valid or not)
        checked_log_path = Path(checked_log_path) if checked_log_path else None
        checked_set = set()
        if checked_log_path and checked_log_path.exists():
            try:
                with open(checked_log_path) as f:
                    data = _json.load(f)
                    checked_set = set(data.get("checked", []))
                logger.info(f"  Loaded {len(checked_set)} previously-checked issue numbers from {checked_log_path}")
            except Exception as e:
                logger.warning(f"  Failed to load checked log: {e}")

        # Combine skip sets: explicit skips + persistent checked log
        skip_issue_numbers = skip_issue_numbers | checked_set

        repo = self.gh.get_repo(f"{owner}/{name}")
        pairs = []
        issues_checked = 0
        issues_skipped_pr = 0
        issues_skipped_existing = 0
        issues_no_link = 0
        issues_filtered = 0
        newly_checked = set()  # numbers checked in THIS run
        start_time = time.time()

        logger.info(f"{'='*60}")
        logger.info(f"Mining {owner}/{name} — target: {max_pairs} pairs")
        if skip_issue_numbers:
            logger.info(f"  Skipping {len(skip_issue_numbers)} previously-seen issues")
        logger.info(f"{'='*60}")

        # Use search API to get only actual issues (not PRs) with linked PRs.
        # GitHub search caps at 1000 results per query, so we paginate with
        # date windows: after exhausting a batch, query for older issues.
        base_query = f"repo:{owner}/{name} is:issue is:closed linked:pr"
        date_cutoff = ""  # empty = no date filter on first pass
        search_exhausted = False

        while len(pairs) < max_pairs and not search_exhausted:
            query = f"{base_query}{date_cutoff}"
            logger.info(f"  Search query: {query}")
            issues = self.gh.search_issues(query=query, sort="updated", order="desc")

            batch_seen = 0
            oldest_updated = None

            try:
                for issue in issues:
                    if len(pairs) >= max_pairs:
                        break

                    batch_seen += 1
                    # Track the oldest updated_at to set next date window
                    if issue.updated_at:
                        if oldest_updated is None or issue.updated_at < oldest_updated:
                            oldest_updated = issue.updated_at

                    # Skip issues we've already evaluated (saves API calls)
                    if issue.number in skip_issue_numbers:
                        issues_skipped_existing += 1
                        continue

                    issues_checked += 1
                    newly_checked.add(issue.number)

                    # Progress every 25 issues checked
                    if issues_checked % 25 == 0:
                        elapsed = time.time() - start_time
                        rate = issues_checked / elapsed * 60 if elapsed > 0 else 0
                        logger.info(f"  [{owner}/{name}] Checked {issues_checked} issues -> {len(pairs)} pairs found ({elapsed:.0f}s elapsed, {rate:.1f} issues/min, {issues_skipped_existing} pre-skipped)")

                        # Periodically persist the checked log so we don't lose progress
                        if checked_log_path and issues_checked % 100 == 0:
                            self._save_checked_log(checked_log_path, checked_set | newly_checked)

                    try:
                        pair = self._try_extract_pair(repo, issue)
                        if pair is None:
                            if issue.pull_request is not None:
                                issues_skipped_pr += 1
                            else:
                                issues_no_link += 1
                            continue

                        if self._passes_filters(pair):
                            pairs.append(pair)
                            logger.info(f"  + Issue #{issue.number} -> PR #{pair.pr_number} ({pair.duration_hours:.1f}h) [{len(pairs)}/{max_pairs}]")

                            # Save after first match to verify saves work, then every 25
                            if save_path and (len(pairs) == 1 or len(pairs) % 25 == 0):
                                self._incremental_save(pairs, save_path, owner, name)
                        else:
                            issues_filtered += 1

                    except RateLimitExceededException:
                        logger.warning(f"  Rate limit hit after {issues_checked} issues, waiting for reset...")
                        self._handle_rate_limit()
                        logger.info(f"  Resuming...")
                    except Exception as e:
                        logger.warning(f"Error processing issue #{issue.number}: {e}")
                        continue

            except RateLimitExceededException:
                logger.warning(f"  Rate limit hit during pagination, waiting for reset...")
                self._handle_rate_limit()
                search_exhausted = True  # restart outer loop cleanly on next call
            except Exception as e:
                logger.warning(f"  Network error during pagination after {issues_checked} issues: {e}")
                logger.warning(f"  Saving progress ({len(pairs)} pairs) and stopping.")
                search_exhausted = True

            # If this batch returned < 1000 results, there are no more issues
            if batch_seen < 1000:
                search_exhausted = True
            elif oldest_updated is not None:
                # Move the window to before the oldest issue we saw
                date_str = oldest_updated.strftime("%Y-%m-%dT%H:%M:%S")
                date_cutoff = f" updated:<{date_str}"
                logger.info(f"  Reached 1000-result cap, paging to issues updated before {date_str}")
            else:
                search_exhausted = True

        elapsed = time.time() - start_time
        logger.info(f"  Summary for {owner}/{name} (completed in {elapsed/60:.1f} min):")
        logger.info(f"    Pre-skipped (already seen): {issues_skipped_existing}")
        logger.info(f"    Issues checked:             {issues_checked}")
        logger.info(f"    Skipped (is PR):            {issues_skipped_pr}")
        logger.info(f"    No linked PR:               {issues_no_link}")
        logger.info(f"    Filtered out:               {issues_filtered}")
        logger.info(f"    Valid pairs:                {len(pairs)}")

        # Final incremental save
        if save_path and pairs:
            self._incremental_save(pairs, save_path, owner, name)

        # Final save of checked log
        if checked_log_path:
            self._save_checked_log(checked_log_path, checked_set | newly_checked)
            logger.info(f"  Checked log updated: {len(checked_set | newly_checked)} total issue numbers tracked")

        return pairs

    def _save_checked_log(self, path, checked_set):
        """Persist the set of checked issue numbers to disk."""
        from pathlib import Path
        import json as _json
        from datetime import datetime as _dt

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "checked": sorted(checked_set),
            "count": len(checked_set),
            "last_updated": _dt.now().isoformat(),
        }
        with open(path, "w") as f:
            _json.dump(data, f)

    def _incremental_save(self, pairs, save_path, owner, name):
        """Save current pairs to disk incrementally."""
        from pathlib import Path
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        df = self.pairs_to_dataframe(pairs)
        try:
            incremental_path = save_path.parent / f"{owner}_{name}_partial.parquet"
            df.to_parquet(incremental_path, index=False)
            logger.info(f"  Saved {len(pairs)} pairs to {incremental_path}")
        except ImportError:
            incremental_path = save_path.parent / f"{owner}_{name}_partial.csv"
            df.to_csv(incremental_path, index=False)
            logger.info(f"  Saved {len(pairs)} pairs to {incremental_path} (CSV fallback)")

    def _try_extract_pair(self, repo, issue) -> IssuePRPair | None:
        """Try to extract a linked issue-PR pair from an issue."""
        # Skip pull requests (GitHub API returns PRs as issues too)
        if issue.pull_request is not None:
            return None

        # Find linked merged PR via timeline events
        linked_pr = self._find_linked_pr(repo, issue)
        if linked_pr is None or not linked_pr.merged:
            return None

        # Get files changed in PR
        pr_files = [f.filename for f in linked_pr.get_files()]

        # Determine assignment time
        assigned_at = self._get_assignment_time(issue)

        # Compute duration
        start_time = assigned_at or issue.created_at
        end_time = linked_pr.merged_at
        if end_time is None:
            return None

        duration_hours = (end_time - start_time).total_seconds() / 3600

        return IssuePRPair(
            repo=f"{repo.owner.login}/{repo.name}",
            issue_number=issue.number,
            issue_title=issue.title or "",
            issue_body=issue.body or "",
            issue_labels=[label.name for label in issue.labels],
            issue_created_at=issue.created_at,
            issue_assigned_at=assigned_at,
            pr_number=linked_pr.number,
            pr_title=linked_pr.title or "",
            pr_body=linked_pr.body or "",
            pr_merged_at=linked_pr.merged_at,
            pr_files_changed=pr_files,
            duration_hours=duration_hours,
        )

    def _find_linked_pr(self, repo, issue):
        """Find a merged PR linked to an issue via timeline events or search fallback."""
        # Try 1: Timeline events (cross-references and close-via-commit)
        try:
            events = issue.get_timeline()
            for event in events:
                if event.event == "cross-referenced" and event.source:
                    source = event.source
                    if hasattr(source, "issue") and source.issue.pull_request:
                        pr = repo.get_pull(source.issue.number)
                        if pr.merged:
                            return pr

                elif event.event == "closed" and event.commit_id:
                    try:
                        commit = repo.get_commit(event.commit_id)
                        for pr in commit.get_pulls():
                            if pr.merged:
                                return pr
                    except RateLimitExceededException:
                        raise
                    except Exception:
                        continue

        except RateLimitExceededException:
            raise
        except Exception as e:
            logger.debug(f"Timeline lookup failed for #{issue.number}: {e}")

        # Try 2: Search for merged PRs that reference this issue number.
        # This catches links that the timeline API misses (common on older issues).
        try:
            results = self.gh.search_issues(
                f"repo:{repo.full_name} is:pr is:merged #{issue.number}"
            )
            for result in results:
                pr = repo.get_pull(result.number)
                if pr.merged:
                    return pr
        except RateLimitExceededException:
            raise
        except Exception as e:
            logger.debug(f"Search fallback failed for #{issue.number}: {e}")

        return None

    def _get_assignment_time(self, issue) -> datetime | None:
        """Get the earliest assignment time for an issue."""
        try:
            for event in issue.get_events():
                if event.event == "assigned":
                    return event.created_at
        except Exception:
            pass
        return None

    def _passes_filters(self, pair: IssuePRPair) -> bool:
        """Apply inclusion/exclusion filters to an issue-PR pair."""
        cfg = self.filter_cfg

        # Check description length
        combined_text = f"{pair.issue_title} {pair.issue_body}"
        if len(combined_text) < cfg["min_description_length"]:
            return False

        # Check duration bounds
        if pair.duration_hours is None:
            return False
        if pair.duration_hours < cfg["min_duration_hours"]:
            return False
        if pair.duration_hours > cfg["max_duration_days"] * 24:
            return False

        # Check excluded labels
        excluded = set(cfg["exclude_labels"])
        if excluded.intersection(pair.issue_labels):
            return False

        return True

    def pairs_to_dataframe(self, pairs: list[IssuePRPair]) -> pd.DataFrame:
        """Convert list of IssuePRPair to a DataFrame."""
        records = []
        for p in pairs:
            records.append({
                "repo": p.repo,
                "issue_number": p.issue_number,
                "issue_title": p.issue_title,
                "issue_body": p.issue_body,
                "issue_labels": "|".join(p.issue_labels),
                "issue_created_at": p.issue_created_at,
                "issue_assigned_at": p.issue_assigned_at,
                "pr_number": p.pr_number,
                "pr_title": p.pr_title,
                "pr_body": p.pr_body,
                "pr_merged_at": p.pr_merged_at,
                "pr_files_changed": "|".join(p.pr_files_changed),
                "num_files_changed": len(p.pr_files_changed),
                "duration_hours": p.duration_hours,
            })
        return pd.DataFrame(records)
