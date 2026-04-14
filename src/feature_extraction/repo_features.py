"""Repository-level feature extraction using PyDriller.

Extracts structural features for each issue-PR pair:
1. Dependency coupling (fan-in/fan-out)
2. Code churn (lines added/modified/deleted in lookback window)
3. Change impact radius (historical co-change patterns)
4. File maturity (age, stability)
"""

import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from pydriller import Repository

from src.utils.config import load_config

logger = logging.getLogger(__name__)


class RepoFeatureExtractor:
    """Extracts repository-level features from local clones."""

    def __init__(self, repo_path: str, config: dict = None):
        self.repo_path = str(repo_path)
        self.config = config or load_config()
        self.repo_cfg = self.config["repo_features"]
        self._coupling_cache = None
        self._churn_cache = None

    def extract_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract repository features for all issue-PR pairs.

        Args:
            df: DataFrame with columns 'issue_created_at', 'pr_files_changed'

        Returns:
            DataFrame with repository feature columns
        """
        import time as _time

        logger.info(f"Extracting repo features for {len(df)} pairs")

        # Pre-compute repository-wide caches
        cache_start = _time.time()
        self._build_caches(df)
        logger.info(f"  Cache build took {_time.time() - cache_start:.1f}s")

        logger.info(f"  Computing features for {len(df)} pairs...")
        features = pd.DataFrame(index=df.index)

        pair_start = _time.time()
        for i, (idx, row) in enumerate(df.iterrows()):
            files = row["pr_files_changed"].split("|") if row["pr_files_changed"] else []
            as_of_date = row["issue_created_at"]

            row_features = self._extract_for_pair(files, as_of_date)
            for key, value in row_features.items():
                features.loc[idx, key] = value

            if (i + 1) % 50 == 0 or (i + 1) == len(df):
                logger.info(f"    Processed {i + 1}/{len(df)} pairs ({_time.time() - pair_start:.0f}s)")

        return features

    def _build_caches(self, df: pd.DataFrame):
        """Pre-compute change coupling and churn data from repository history."""
        earliest_date = pd.to_datetime(df["issue_created_at"]).min()
        lookback = timedelta(days=self.repo_cfg["churn_lookback_days"])
        since = earliest_date - lookback

        logger.info(f"Building repo caches from {since} onward")

        # Track file co-changes and churn
        co_changes = defaultdict(Counter)
        churn_data = defaultdict(lambda: {"added": 0, "deleted": 0, "commits": 0})
        file_first_seen = {}
        file_last_modified = {}

        commit_count = 0
        for commit in Repository(self.repo_path, since=since).traverse_commits():
            commit_count += 1
            if commit_count % 500 == 0:
                logger.info(f"    Processed {commit_count} commits ({len(churn_data)} files tracked so far)")

            changed_files = [m.new_path or m.old_path for m in commit.modified_files]

            # Record co-changes
            for i, f1 in enumerate(changed_files):
                for f2 in changed_files[i + 1 :]:
                    co_changes[f1][f2] += 1
                    co_changes[f2][f1] += 1

            # Record churn per file
            for mod in commit.modified_files:
                path = mod.new_path or mod.old_path
                churn_data[path]["added"] += mod.added_lines
                churn_data[path]["deleted"] += mod.deleted_lines
                churn_data[path]["commits"] += 1

                if path not in file_first_seen:
                    file_first_seen[path] = commit.committer_date
                file_last_modified[path] = commit.committer_date

        logger.info(f"    Done: traversed {commit_count} commits total")

        self._co_changes = co_changes
        self._churn_data = churn_data
        self._file_first_seen = file_first_seen
        self._file_last_modified = file_last_modified

        logger.info(f"Cache built: {len(churn_data)} files tracked")

    def _extract_for_pair(self, files: list[str], as_of_date) -> dict:
        """Extract features for a single issue-PR pair."""
        if not files:
            return self._empty_features()

        # Dependency coupling
        fan_in, fan_out = self._compute_coupling(files)

        # Code churn
        total_added = sum(self._churn_data.get(f, {}).get("added", 0) for f in files)
        total_deleted = sum(self._churn_data.get(f, {}).get("deleted", 0) for f in files)
        total_commits = sum(self._churn_data.get(f, {}).get("commits", 0) for f in files)

        # Change impact radius
        impacted_files = set()
        min_support = self.repo_cfg["coupling_min_support"]
        for f in files:
            for co_file, count in self._co_changes.get(f, {}).items():
                if count >= min_support:
                    impacted_files.add(co_file)
        impact_radius = len(impacted_files - set(files))

        # File maturity
        ages = []
        change_frequencies = []
        for f in files:
            if f in self._file_first_seen:
                age_days = (as_of_date - self._file_first_seen[f]).total_seconds() / 86400
                ages.append(max(age_days, 0))
                change_frequencies.append(self._churn_data.get(f, {}).get("commits", 0))
            else:
                ages.append(0)
                change_frequencies.append(0)

        return {
            "num_files": len(files),
            "fan_in": fan_in,
            "fan_out": fan_out,
            "total_churn_added": total_added,
            "total_churn_deleted": total_deleted,
            "total_churn_commits": total_commits,
            "avg_churn_per_file": (total_added + total_deleted) / max(len(files), 1),
            "change_impact_radius": impact_radius,
            "avg_file_age_days": np.mean(ages) if ages else 0,
            "min_file_age_days": np.min(ages) if ages else 0,
            "max_file_age_days": np.max(ages) if ages else 0,
            "avg_change_frequency": np.mean(change_frequencies) if change_frequencies else 0,
            "max_change_frequency": np.max(change_frequencies) if change_frequencies else 0,
        }

    def _compute_coupling(self, files: list[str]) -> tuple[int, int]:
        """Compute fan-in and fan-out for a set of files.

        Fan-in: number of other files that co-change WITH these files
        Fan-out: number of files these files co-change with
        """
        min_support = self.repo_cfg["coupling_min_support"]
        incoming = set()
        outgoing = set()

        for f in files:
            for co_file, count in self._co_changes.get(f, {}).items():
                if count >= min_support:
                    if co_file not in files:
                        outgoing.add(co_file)
                    incoming.add(co_file)

        return len(incoming), len(outgoing)

    @staticmethod
    def _empty_features() -> dict:
        """Return zero-valued features when no files are available."""
        return {
            "num_files": 0,
            "fan_in": 0,
            "fan_out": 0,
            "total_churn_added": 0,
            "total_churn_deleted": 0,
            "total_churn_commits": 0,
            "avg_churn_per_file": 0,
            "change_impact_radius": 0,
            "avg_file_age_days": 0,
            "min_file_age_days": 0,
            "max_file_age_days": 0,
            "avg_change_frequency": 0,
            "max_change_frequency": 0,
        }
