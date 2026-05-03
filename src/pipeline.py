"""Main pipeline orchestrating the full SE3M replication study.

Usage:
    python -m src.pipeline --step validate       # Step 1: Validate target repos
    python -m src.pipeline --step collect        # Step 2: Mine issue-PR pairs
    python -m src.pipeline --step features       # Step 3: Extract all features (NLP + repo)
    python -m src.pipeline --step nlp_features   # Step 3a: NLP features only (CodeBERT)
    python -m src.pipeline --step repo_features  # Step 3b: Repo features only (PyDriller)
    python -m src.pipeline --step train          # Step 4: Train and evaluate models
    python -m src.pipeline --step analyze        # Step 5: SHAP + error analysis
    python -m src.pipeline --step all            # Run full pipeline
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.config import get_data_dir, get_model_dir, load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log"),
    ],
)
logger = logging.getLogger(__name__)


def step_validate(config: dict):
    """Step 1: Validate target repositories against inclusion criteria."""
    from src.data_collection.github_miner import GitHubMiner

    miner = GitHubMiner(config)
    results = []

    for repo in config["repositories"]:
        result = miner.validate_repository(repo["owner"], repo["name"])
        results.append(result)
        status = "PASS" if result["passes_all"] else "FAIL"
        logger.info(f"  {result['repo']}: {status}")

    # Save validation results
    out_path = get_data_dir() / "repo_validation.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Validation results saved to {out_path}")
    return results


def step_clean_data(config: dict):
    """Step 1.5: Clean raw dataset by removing known data quality issues.

    Removes:
    - Repos with < 10 samples (stray/singleton repos)
    - Empty issue bodies (no text = no signal for NLP)
    - Samples with 0 files changed (likely data errors)
    - Duplicate repo+issue_number pairs

    Saves cleaned data back to the same file (backs up original first).
    """
    import shutil

    data_dir = get_data_dir()
    df = _load_raw_data()
    n_original = len(df)

    logger.info(f"{'='*60}")
    logger.info(f"Cleaning dataset: {n_original} samples")
    logger.info(f"{'='*60}")

    # 1. Remove repos with < 10 samples
    repo_counts = df["repo"].value_counts()
    small_repos = repo_counts[repo_counts < 10].index.tolist()
    if small_repos:
        n_before = len(df)
        df = df[~df["repo"].isin(small_repos)]
        logger.info(f"  Dropped {n_before - len(df)} samples from small repos: {small_repos}")

    # 2. Remove empty issue bodies
    empty_body_mask = df["issue_body"].fillna("").str.strip() == ""
    n_empty = empty_body_mask.sum()
    if n_empty > 0:
        df = df[~empty_body_mask]
        logger.info(f"  Dropped {n_empty} samples with empty issue_body")

    # 3. Remove 0 files changed
    if "num_files_changed" in df.columns:
        zero_files = (df["num_files_changed"] == 0).sum()
        if zero_files > 0:
            df = df[df["num_files_changed"] > 0]
            logger.info(f"  Dropped {zero_files} samples with 0 files changed")

    # 4. Standardize duration measurement
    # Use issue_created_at → pr_merged_at for ALL pairs (consistent measurement).
    # Previously, pairs with issue_assigned_at used assignment→merge while others
    # used creation→merge, mixing two different duration definitions.
    if "issue_created_at" in df.columns and "pr_merged_at" in df.columns:
        has_assigned = df["issue_assigned_at"].notna().sum() if "issue_assigned_at" in df.columns else 0
        created = pd.to_datetime(df["issue_created_at"])
        merged = pd.to_datetime(df["pr_merged_at"])
        df["duration_hours"] = (merged - created).dt.total_seconds() / 3600
        logger.info(f"  Standardized duration: issue_created_at -> pr_merged_at for all {len(df)} pairs")
        logger.info(f"    (previously {has_assigned} used assignment time, {len(df) - has_assigned} used creation time)")

    # 5. Deduplicate
    n_before = len(df)
    df = df.drop_duplicates(subset=["repo", "issue_number"], keep="first")
    n_dupes = n_before - len(df)
    if n_dupes > 0:
        logger.info(f"  Dropped {n_dupes} duplicate repo+issue_number pairs")

    # 6. Re-apply duration filter (some may now be negative or out of bounds)
    dur_before = len(df)
    df = df[df["duration_hours"] > 0]
    if len(df) < dur_before:
        logger.info(f"  Dropped {dur_before - len(df)} samples with non-positive standardized duration")

    df = df.reset_index(drop=True)
    n_final = len(df)
    n_removed = n_original - n_final

    logger.info(f"\n  Summary: {n_original} -> {n_final} samples ({n_removed} removed, {n_removed/n_original*100:.1f}%)")

    # Show final per-repo breakdown
    logger.info(f"\n  Final per-repo distribution:")
    for repo, count in df["repo"].value_counts().items():
        logger.info(f"    {repo}: {count} ({count/n_final*100:.1f}%)")

    # Backup original and save cleaned version
    raw_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    backup_path = data_dir / "raw" / "issue_pr_pairs_pre_clean.parquet"

    if raw_path.exists() and not backup_path.exists():
        shutil.copy2(raw_path, backup_path)
        logger.info(f"\n  Original backed up to {backup_path}")

    try:
        df.to_parquet(raw_path, index=False)
    except ImportError:
        csv_path = raw_path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        raw_path = csv_path

    logger.info(f"  Cleaned data saved to {raw_path}")
    logger.info(f"\n  NEXT STEPS: re-extract features and retrain:")
    logger.info(f"    python -m src.pipeline --step nlp_features")
    logger.info(f"    python -m src.pipeline --step train")
    logger.info(f"{'='*60}")

    return df


def step_collect(config: dict):
    """Step 2: Mine issue-PR pairs from validated repositories."""
    from src.data_collection.github_miner import GitHubMiner

    import time as _time
    collect_start = _time.time()

    miner = GitHubMiner(config)
    all_pairs = []

    out_path = get_data_dir() / "raw" / "issue_pr_pairs.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing data to append to (if any)
    existing_df = None
    existing_issue_keys = set()
    try:
        existing_df = _load_raw_data()
        existing_issue_keys = set(
            existing_df["repo"] + "#" + existing_df["issue_number"].astype(str)
        )
        logger.info(f"Found existing dataset with {len(existing_df)} pairs")
    except FileNotFoundError:
        logger.info("No existing dataset found, starting fresh")

    # Only collect from repos that passed validation
    validation_path = get_data_dir() / "repo_validation.json"
    valid_repos = set()
    if validation_path.exists():
        import json
        with open(validation_path) as f:
            for r in json.load(f):
                if r.get("passes_all"):
                    valid_repos.add(r["repo"])

    checked_dir = get_data_dir() / "raw" / "checked"
    checked_dir.mkdir(parents=True, exist_ok=True)

    for repo in config["repositories"]:
        repo_full = f"{repo['owner']}/{repo['name']}"
        if valid_repos and repo_full not in valid_repos:
            logger.info(f"Skipping {repo_full} (did not pass validation)")
            continue

        # Count how many we already have for this repo
        existing_for_repo = sum(1 for k in existing_issue_keys if k.startswith(repo_full + "#"))
        target = config["filtering"]["target_sample_size"]
        remaining = target - existing_for_repo

        if remaining <= 0:
            logger.info(f"Already have {existing_for_repo}/{target} pairs for {repo_full}, skipping")
            continue

        # Build skip set: issue numbers we already have for this repo
        skip_numbers = set()
        if existing_df is not None:
            repo_existing = existing_df[existing_df["repo"] == repo_full]
            skip_numbers = set(repo_existing["issue_number"].tolist())

        # Per-repo checked log (tracks all evaluated issues, valid or not)
        checked_log_path = checked_dir / f"{repo['owner']}_{repo['name']}_checked.json"

        logger.info(f"Have {existing_for_repo} pairs for {repo_full}, collecting {remaining} more")
        pairs = miner.mine_issue_pr_pairs(
            repo["owner"], repo["name"],
            max_pairs=remaining,
            save_path=out_path,
            skip_issue_numbers=skip_numbers,
            checked_log_path=checked_log_path,
        )
        all_pairs.extend(pairs)

    new_df = miner.pairs_to_dataframe(all_pairs)

    # Merge with existing data, dedup by repo+issue_number
    if existing_df is not None and len(new_df) > 0:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["repo", "issue_number"], keep="first")
        df = combined_df
        logger.info(f"Merged: {len(existing_df)} existing + {len(new_df)} new = {len(df)} total (after dedup)")
    elif existing_df is not None:
        df = existing_df
    else:
        df = new_df

    # Save final combined dataset
    try:
        df.to_parquet(out_path, index=False)
        saved_path = out_path
    except ImportError:
        saved_path = out_path.with_suffix(".csv")
        df.to_csv(saved_path, index=False)
        logger.info("  (Saved as CSV -- install pyarrow for parquet support)")

    total_elapsed = _time.time() - collect_start
    logger.info(f"{'='*60}")
    logger.info(f"Collection complete: {len(df)} total issue-PR pairs")
    logger.info(f"Total time: {total_elapsed/60:.1f} minutes")
    logger.info(f"Saved to {saved_path}")
    logger.info(f"{'='*60}")
    if len(df) > 0:
        logger.info(f"Duration stats:\n{df['duration_hours'].describe()}")
    return df


def step_merge_data(config: dict, merge_path: str = None):
    """Merge another collector's dataset into your own.

    Loads the other dataset (parquet or CSV), concatenates with your existing
    data, deduplicates by repo+issue_number, and saves back to the main file.

    Usage:
        python -m src.pipeline --step merge_data --merge-from path/to/other_data.parquet
    """
    from pathlib import Path

    if not merge_path:
        raise ValueError("merge_data requires --merge-from <path>")

    merge_path = Path(merge_path)
    if not merge_path.exists():
        raise FileNotFoundError(f"Merge file not found: {merge_path}")

    # Load partner's data
    if merge_path.suffix == ".parquet":
        partner_df = pd.read_parquet(merge_path)
    elif merge_path.suffix == ".csv":
        partner_df = pd.read_csv(merge_path)
    else:
        raise ValueError(f"Unsupported file format: {merge_path.suffix}")

    logger.info(f"Loaded {len(partner_df)} pairs from {merge_path}")

    # Show breakdown by repo
    logger.info("Partner data by repo:")
    for repo, count in partner_df["repo"].value_counts().items():
        logger.info(f"  {repo}: {count}")

    # Load existing data (if any)
    out_path = get_data_dir() / "raw" / "issue_pr_pairs.parquet"
    try:
        existing_df = _load_raw_data()
        logger.info(f"Loaded {len(existing_df)} existing pairs")
    except FileNotFoundError:
        existing_df = None
        logger.info("No existing dataset, partner data will become the new dataset")

    # Merge with dedup
    if existing_df is not None:
        combined = pd.concat([existing_df, partner_df], ignore_index=True)
        before = len(combined)
        combined = combined.drop_duplicates(subset=["repo", "issue_number"], keep="first")
        after = len(combined)
        logger.info(f"Merged: {len(existing_df)} existing + {len(partner_df)} partner = {before}")
        logger.info(f"After dedup: {after} unique pairs (removed {before - after} duplicates)")
    else:
        combined = partner_df

    # Save
    try:
        combined.to_parquet(out_path, index=False)
        saved_path = out_path
    except ImportError:
        saved_path = out_path.with_suffix(".csv")
        combined.to_csv(saved_path, index=False)

    logger.info(f"{'='*60}")
    logger.info(f"Merge complete: {len(combined)} total pairs saved to {saved_path}")
    logger.info("Combined data by repo:")
    for repo, count in combined["repo"].value_counts().items():
        logger.info(f"  {repo}: {count}")
    logger.info(f"{'='*60}")
    return combined


def _load_raw_data():
    """Load the raw issue-PR pairs dataset (parquet or CSV)."""
    data_dir = get_data_dir()
    parquet_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    csv_path = data_dir / "raw" / "issue_pr_pairs.csv"

    if parquet_path.exists():
        logger.info(f"Loading raw data from {parquet_path}")
        return pd.read_parquet(parquet_path)
    elif csv_path.exists():
        logger.info(f"Loading raw data from {csv_path}")
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(
            f"No raw data found. Run 'python -m src.pipeline --step collect' first.\n"
            f"Looked for: {parquet_path} and {csv_path}"
        )


def _save_features(df, path):
    """Save feature DataFrame with parquet/CSV fallback."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(path, index=False)
        logger.info(f"Saved to {path}")
    except ImportError:
        csv_path = path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved to {csv_path} (CSV fallback)")


def _encoder_slug(config: dict) -> str:
    """Slug representing the NLP encoder, for per-encoder cache files."""
    name = config.get("nlp", {}).get("model_name", "microsoft/codebert-base")
    return name.replace("/", "__").replace(" ", "_")


def step_nlp_features(config: dict):
    """Step 3a: Extract NLP features (encoder embeddings + derived).

    Writes to a per-encoder file so swapping encoders doesn't overwrite
    prior results. Also maintains a "nlp_features.parquet" symlink-like
    copy that matches the current config so training/analyze keep working.
    """
    import time as _time
    import shutil
    from src.feature_extraction.nlp_features import NLPFeatureExtractor

    start = _time.time()
    data_dir = get_data_dir()
    df = _load_raw_data()

    slug = _encoder_slug(config)
    logger.info(f"{'='*60}")
    logger.info(f"Extracting NLP features for {len(df)} issue-PR pairs")
    logger.info(f"  Encoder: {config['nlp']['model_name']} (slug: {slug})")
    logger.info(f"{'='*60}")

    nlp_extractor = NLPFeatureExtractor(config)
    nlp_features = nlp_extractor.extract_all_features(df)

    # Per-encoder cache file
    encoder_path = data_dir / "processed" / f"nlp_features__{slug}.parquet"
    _save_features(nlp_features, encoder_path)

    # Also write the canonical "active" file that downstream steps read
    active_path = data_dir / "processed" / "nlp_features.parquet"
    try:
        nlp_features.to_parquet(active_path, index=False)
    except ImportError:
        nlp_features.to_csv(active_path.with_suffix(".csv"), index=False)
    logger.info(f"Active nlp_features.parquet updated to {slug}")

    elapsed = _time.time() - start
    logger.info(f"{'='*60}")
    logger.info(f"NLP features complete: {nlp_features.shape} in {elapsed/60:.1f} min")
    logger.info(f"{'='*60}")
    return nlp_features


def step_repo_features(config: dict):
    """Step 3b: Extract repository-mined structural features."""
    import time as _time
    from src.data_collection.repo_cloner import RepoCloner
    from src.feature_extraction.repo_features import RepoFeatureExtractor

    start = _time.time()
    data_dir = get_data_dir()
    df = _load_raw_data()

    logger.info(f"{'='*60}")
    logger.info(f"Extracting repo features for {len(df)} issue-PR pairs")
    logger.info(f"{'='*60}")

    cloner = RepoCloner()
    all_repo_features = []

    # Per-repo caching: save each repo's features separately so
    # if the process is interrupted, completed repos don't have to be redone
    per_repo_dir = data_dir / "processed" / "repo_features_by_repo"
    per_repo_dir.mkdir(parents=True, exist_ok=True)

    for repo in config["repositories"]:
        repo_full = f"{repo['owner']}/{repo['name']}"
        repo_df = df[df["repo"] == repo_full].copy()

        if len(repo_df) == 0:
            logger.info(f"  No pairs for {repo_full}, skipping")
            continue

        per_repo_path = per_repo_dir / f"{repo['owner']}_{repo['name']}.parquet"
        cached_features = None
        cached_issue_numbers = set()

        # Load existing cached features if any
        if per_repo_path.exists():
            try:
                cached_features = pd.read_parquet(per_repo_path)
                if "issue_number" in cached_features.columns:
                    cached_issue_numbers = set(cached_features["issue_number"].tolist())
                    logger.info(f"  {repo_full}: found cache with {len(cached_features)} rows "
                                f"({len(cached_issue_numbers)} unique issues)")
                else:
                    # Old cache format without issue_number — invalidate it
                    logger.warning(f"  {repo_full}: old cache format, will recompute")
                    cached_features = None
            except Exception as e:
                logger.warning(f"  {repo_full}: failed to load cache: {e}")
                cached_features = None

        # Figure out which pairs need new features
        missing_df = repo_df[~repo_df["issue_number"].isin(cached_issue_numbers)]

        if len(missing_df) == 0:
            logger.info(f"  {repo_full}: all {len(repo_df)} pairs already have cached features, skipping")
            # Keep only the rows we need from the cache
            relevant = cached_features[cached_features["issue_number"].isin(repo_df["issue_number"])]
            all_repo_features.append(relevant)
            continue

        logger.info(f"  {repo_full}: need features for {len(missing_df)} new pairs "
                    f"(out of {len(repo_df)} total)")

        repo_path = cloner.clone_or_update(repo["owner"], repo["name"])
        extractor = RepoFeatureExtractor(repo_path, config)
        new_features = extractor.extract_all_features(missing_df)

        # Attach issue_number so we can dedup / lookup later
        new_features = new_features.reset_index(drop=True)
        new_features.insert(0, "issue_number", missing_df["issue_number"].values)

        # Merge with existing cache
        if cached_features is not None and len(cached_features) > 0:
            combined = pd.concat([cached_features, new_features], ignore_index=True)
            combined = combined.drop_duplicates(subset=["issue_number"], keep="last")
        else:
            combined = new_features

        # Save updated cache
        try:
            combined.to_parquet(per_repo_path, index=False)
            logger.info(f"  Saved {repo_full} features to {per_repo_path} ({len(combined)} rows)")
        except Exception as e:
            logger.warning(f"  Could not save checkpoint: {e}")

        # Only keep rows relevant to the current dataset, tag with repo
        relevant = combined[combined["issue_number"].isin(repo_df["issue_number"])].copy()
        relevant["repo"] = repo_full
        all_repo_features.append(relevant)

    # Combine all repos; align with main df order via merge
    raw_features = pd.concat(all_repo_features, ignore_index=True)

    # Merge on (repo, issue_number) to preserve the order of df
    key_df = df[["repo", "issue_number"]].copy()
    repo_features = key_df.merge(
        raw_features, on=["repo", "issue_number"], how="left"
    )
    # Drop the key columns so feature matrix only has numeric features
    repo_features = repo_features.drop(columns=["repo", "issue_number"])

    out_path = data_dir / "processed" / "repo_features.parquet"
    _save_features(repo_features, out_path)

    elapsed = _time.time() - start
    logger.info(f"{'='*60}")
    logger.info(f"Repo features complete: {repo_features.shape} in {elapsed/60:.1f} min")
    logger.info(f"{'='*60}")
    return repo_features


def step_features(config: dict):
    """Step 3: Extract all features (NLP + repository)."""
    nlp_features = step_nlp_features(config)
    repo_features = step_repo_features(config)
    return nlp_features, repo_features


def _load_features(name):
    """Load a processed feature file (parquet or CSV)."""
    data_dir = get_data_dir()
    parquet_path = data_dir / "processed" / f"{name}.parquet"
    csv_path = data_dir / "processed" / f"{name}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(
            f"No feature file found for '{name}'. "
            f"Run the appropriate feature extraction step first.\n"
            f"Looked for: {parquet_path} and {csv_path}"
        )


def _apply_duration_filter(df, features, config):
    """Filter samples by duration bounds from config, keeping df and features aligned."""
    max_hours = config["filtering"]["max_duration_days"] * 24
    min_hours = config["filtering"]["min_duration_hours"]

    mask = (df["duration_hours"] >= min_hours) & (df["duration_hours"] <= max_hours)
    n_before = len(df)
    df_filtered = df[mask].reset_index(drop=True)
    features_filtered = features[mask].reset_index(drop=True)
    n_after = len(df_filtered)

    if n_before != n_after:
        logger.info(f"  Duration filter: {n_before} -> {n_after} samples "
                     f"(removed {n_before - n_after} outside [{min_hours}h, {max_hours}h])")
    else:
        logger.info(f"  Duration filter: all {n_after} samples within bounds")

    return df_filtered, features_filtered


def step_train_model_a(config: dict):
    """Step 4a: Train Model A — Text-only (CodeBERT embeddings + derived NLP features)."""
    from src.modeling.trainer import ModelTrainer

    df = _load_raw_data()
    nlp_features = _load_features("nlp_features")

    # Apply duration filter (may be tighter than what was used during collection)
    df, nlp_features = _apply_duration_filter(df, nlp_features, config)
    y = df["duration_hours"]

    trainer = ModelTrainer(config)
    result_a = trainer.train_and_evaluate(nlp_features, y, "model_a_text_only")
    return result_a


def step_train_model_b_no_numfiles(config: dict):
    """Train Model B without num_files to test if PyDriller metrics carry signal.

    num_files dominates Model B's SHAP importance (16x the next feature)
    and is also a post-hoc signal (derived from pr_files_changed, not
    available at issue-creation time). This step removes it to see if
    the structural metrics (churn, coupling, file age) predict anything.
    """
    from src.modeling.trainer import ModelTrainer

    df = _load_raw_data()
    repo_features = _load_features("repo_features")

    # Apply duration filter
    max_hours = config["filtering"]["max_duration_days"] * 24
    min_hours = config["filtering"]["min_duration_hours"]
    mask = (df["duration_hours"] >= min_hours) & (df["duration_hours"] <= max_hours)
    keep_idx = mask[mask].index.tolist()
    df = df.loc[keep_idx].reset_index(drop=True)
    repo_features = repo_features.iloc[keep_idx].reset_index(drop=True)
    y = df["duration_hours"]

    # Drop num_files
    if "num_files" in repo_features.columns:
        repo_features = repo_features.drop(columns=["num_files"])
        logger.info(f"  Dropped num_files. Remaining features: {list(repo_features.columns)}")
    else:
        logger.warning("  num_files column not found in repo_features")

    trainer = ModelTrainer(config)
    result = trainer.train_and_evaluate(repo_features, y, "model_b_repo_no_numfiles")

    # Print comparison with original Model B
    original_path = get_model_dir() / "model_b_repo_only" / "results.json"
    if original_path.exists():
        with open(original_path) as f:
            original = json.load(f).get("test_metrics", {})

        new = result.test_metrics
        print()
        print("=" * 70)
        print("MODEL B: WITH vs WITHOUT num_files")
        print("=" * 70)
        print(f"  {'Metric':<12} {'With num_files':>15} {'Without':>15} {'Delta':>12}")
        print(f"  {'-'*55}")
        for key, label in [("mae", "MAE"), ("mdae", "MdAE"), ("sa", "SA"),
                            ("pred_25", "PRED(25)"), ("r2", "R2"),
                            ("glass_delta", "Glass delta")]:
            orig_val = original.get(key, 0)
            new_val = new.get(key, 0)
            delta = new_val - orig_val
            sign = "+" if delta > 0 else ""
            print(f"  {label:<12} {orig_val:>15.2f} {new_val:>15.2f} {sign}{delta:>11.2f}")
        print()

    # Quick feature importance from XGBoost (no SHAP needed)
    import joblib
    model_path = get_model_dir() / "model_b_repo_no_numfiles" / "model.joblib"
    if model_path.exists():
        model = joblib.load(model_path)
        importances = model.feature_importances_
        feature_names = result.feature_names
        imp_pairs = sorted(zip(feature_names, importances), key=lambda x: -x[1])
        print("  Top features (XGBoost gain) without num_files:")
        for fname, imp in imp_pairs[:5]:
            print(f"    {fname}: {imp:.4f}")
        print()

    return result


def step_train(config: dict):
    """Step 4: Train Models A, B, C and compare."""
    from src.modeling.trainer import ModelTrainer

    df = _load_raw_data()
    nlp_features = _load_features("nlp_features")

    # Apply duration filter to all models consistently
    max_hours = config["filtering"]["max_duration_days"] * 24
    min_hours = config["filtering"]["min_duration_hours"]
    mask = (df["duration_hours"] >= min_hours) & (df["duration_hours"] <= max_hours)
    keep_idx = mask[mask].index.tolist()
    n_before = len(df)
    df = df.loc[keep_idx].reset_index(drop=True)
    nlp_features = nlp_features.iloc[keep_idx].reset_index(drop=True)
    n_after = len(df)
    if n_before != n_after:
        logger.info(f"  Duration filter: {n_before} -> {n_after} samples "
                     f"(removed {n_before - n_after} outside [{min_hours}h, {max_hours}h])")

    y = df["duration_hours"]
    trainer = ModelTrainer(config)

    # Model A: Text-only
    result_a = trainer.train_and_evaluate(nlp_features, y, "model_a_text_only")

    # Model B: Repo-only (skip if not yet extracted)
    try:
        repo_features = _load_features("repo_features")
        repo_features = repo_features.iloc[keep_idx].reset_index(drop=True)
        result_b = trainer.train_and_evaluate(repo_features, y, "model_b_repo_only")

        # Model C: Combined
        combined = pd.concat([nlp_features, repo_features], axis=1)
        result_c = trainer.train_and_evaluate(combined, y, "model_c_combined")

        # Statistical comparison
        comparisons = trainer.compare_models(result_a, result_b, result_c)

        results = {
            "model_a": result_a.test_metrics,
            "model_b": result_b.test_metrics,
            "model_c": result_c.test_metrics,
            "comparisons": comparisons,
        }
    except FileNotFoundError:
        logger.warning("Repo features not found -- skipping Models B and C")
        results = {"model_a": result_a.test_metrics}

    out_path = get_model_dir() / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {out_path}")
    return results


def step_dimensionality_sweep(config: dict):
    """Sweep PCA dimensionality across 7 values from 50 to 768.

    Fine-grained benchmark of how prediction accuracy varies with the
    PCA feature budget. Covers evenly-spaced points plus NONE-774 for
    the upper bound. Useful for plotting the accuracy-vs-dimensions curve.
    """
    import copy
    import time as _time
    from src.modeling.trainer import ModelTrainer

    # Evenly-spaced sweep: 50 → 650 in 6 steps, plus NONE for full 768
    configurations = [
        ("pca", 50),
        ("pca", 170),
        ("pca", 290),
        ("pca", 410),
        ("pca", 530),
        ("pca", 650),
        ("none", 768),
    ]

    start = _time.time()
    df = _load_raw_data()
    nlp = _load_features("nlp_features")
    df, nlp = _apply_duration_filter(df, nlp, config)
    y = df["duration_hours"]

    logger.info(f"{'='*80}")
    logger.info(f"DIMENSIONALITY SWEEP — {len(configurations)} configurations × {len(df)} samples")
    logger.info(f"  Estimated total runtime: 2-3 hours (larger K = longer training)")
    logger.info(f"{'='*80}")

    results = {}
    for method, k in configurations:
        label = f"{method.upper()}-{k}" if method != "none" else "NONE-768"
        logger.info(f"\n[{label}] Starting...")

        cfg = copy.deepcopy(config)
        cfg.setdefault("feature_selection", {})["method"] = method
        if method == "pca":
            cfg.setdefault("pca", {})["n_components"] = k

        trainer = ModelTrainer(cfg)
        result = trainer.train_and_evaluate(
            nlp, y, f"dim_sweep_{method}_{k}"
        )
        results[label] = result.test_metrics

    # Print comparison
    print()
    print("=" * 88)
    print("DIMENSIONALITY SWEEP — TEST METRICS FOR MODEL A")
    print("=" * 88)
    print(f"{'Config':<12} {'MAE':>10} {'MdAE':>10} {'PRED25':>9} {'PRED50':>9} {'R2':>10} {'SA':>9}")
    print("-" * 88)
    for label, metrics in results.items():
        print(f"{label:<12} "
              f"{metrics.get('mae', 0):>10.2f} "
              f"{metrics.get('mdae', 0):>10.2f} "
              f"{metrics.get('pred_25', 0):>8.2f}% "
              f"{metrics.get('pred_50', 0):>8.2f}% "
              f"{metrics.get('r2', 0):>10.4f} "
              f"{metrics.get('sa', 0):>8.2f}%")
    print()

    # Save
    out_path = get_model_dir() / "dimensionality_sweep.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved results to {out_path}")
    logger.info(f"Total time: {(_time.time() - start)/60:.1f} min")


def step_feature_selection_ablation(config: dict):
    """Compare PCA vs Top-K feature selection at multiple K values.

    Runs Model A with each (method, k) combination and prints a
    side-by-side metrics table. Helps answer: does supervised feature
    selection (Top-K by F-statistic) beat unsupervised PCA at the same
    feature budget?
    """
    import copy
    import time as _time
    from src.modeling.trainer import ModelTrainer

    configurations = [
        ("pca", 20),
        ("pca", 50),
        ("pls", 20),
        ("pls", 50),
        ("topk", 20),
        ("topk", 50),
        ("none", 768),
    ]

    start = _time.time()
    df = _load_raw_data()
    nlp = _load_features("nlp_features")
    df, nlp = _apply_duration_filter(df, nlp, config)
    y = df["duration_hours"]

    logger.info(f"{'='*80}")
    logger.info(f"FEATURE SELECTION ABLATION — {len(configurations)} configurations × {len(df)} samples")
    logger.info(f"{'='*80}")

    results = {}
    for method, k in configurations:
        label = f"{method.upper()}-{k}" if method != "none" else "NONE-768"
        logger.info(f"\n[{label}] Starting...")

        cfg = copy.deepcopy(config)
        cfg.setdefault("feature_selection", {})["method"] = method
        if method == "pca":
            cfg.setdefault("pca", {})["n_components"] = k
        elif method == "topk":
            cfg.setdefault("topk", {})["k"] = k
        elif method == "pls":
            cfg.setdefault("pls", {})["n_components"] = k

        trainer = ModelTrainer(cfg)
        result = trainer.train_and_evaluate(
            nlp, y, f"feature_sel_{method}_{k}"
        )
        results[label] = result.test_metrics

    # Print comparison
    print()
    print("=" * 88)
    print("FEATURE SELECTION ABLATION — TEST METRICS FOR MODEL A")
    print("=" * 88)
    print(f"{'Config':<12} {'MAE':>10} {'MdAE':>10} {'PRED25':>9} {'PRED50':>9} {'R2':>10} {'SA':>9}")
    print("-" * 88)
    for label, metrics in results.items():
        print(f"{label:<12} "
              f"{metrics.get('mae', 0):>10.2f} "
              f"{metrics.get('mdae', 0):>10.2f} "
              f"{metrics.get('pred_25', 0):>8.2f}% "
              f"{metrics.get('pred_50', 0):>8.2f}% "
              f"{metrics.get('r2', 0):>10.4f} "
              f"{metrics.get('sa', 0):>8.2f}%")
    print()

    # Save
    out_path = get_model_dir() / "feature_selection_ablation.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved results to {out_path}")
    logger.info(f"Total time: {(_time.time() - start)/60:.1f} min")


def step_encoder_ablation(config: dict, encoders: list = None):
    """Run Model A training with multiple encoders and compare.

    For each encoder:
      1. Extract NLP features using that encoder
      2. Train Model A
      3. Record test metrics

    Prints a side-by-side comparison at the end. Results for each
    encoder are saved to models/model_a_text_only__<slug>/
    """
    import copy
    import time as _time
    from src.feature_extraction.nlp_features import NLPFeatureExtractor
    from src.modeling.trainer import ModelTrainer

    if encoders is None:
        encoders = [
            "microsoft/codebert-base",
            "microsoft/unixcoder-base",
            "BAAI/bge-base-en-v1.5",
        ]

    start = _time.time()
    data_dir = get_data_dir()
    df = _load_raw_data()

    # Apply duration filter to the dataset
    max_hours = config["filtering"]["max_duration_days"] * 24
    min_hours = config["filtering"]["min_duration_hours"]
    mask = (df["duration_hours"] >= min_hours) & (df["duration_hours"] <= max_hours)
    df = df[mask].reset_index(drop=True)
    y = df["duration_hours"]

    logger.info(f"{'='*72}")
    logger.info(f"ENCODER ABLATION — {len(encoders)} encoders x {len(df)} samples")
    logger.info(f"{'='*72}")

    results = {}
    for i, encoder_name in enumerate(encoders, 1):
        logger.info(f"\n[{i}/{len(encoders)}] Encoder: {encoder_name}")
        cfg = copy.deepcopy(config)
        cfg.setdefault("nlp", {})["model_name"] = encoder_name

        # Extract features (per-encoder cache)
        slug = _encoder_slug(cfg)
        cache_path = data_dir / "processed" / f"nlp_features__{slug}.parquet"

        if cache_path.exists():
            logger.info(f"  Using cached features from {cache_path}")
            features = pd.read_parquet(cache_path)
            if len(features) != len(df):
                logger.info(f"  Cached length mismatch ({len(features)} vs {len(df)}), recomputing")
                features = None
        else:
            features = None

        if features is None:
            extractor = NLPFeatureExtractor(cfg)
            features = extractor.extract_all_features(df)
            _save_features(features, cache_path)

        # Train Model A with a unique name so we don't overwrite
        model_name = f"model_a_text_only__{slug}"
        trainer = ModelTrainer(cfg)
        result = trainer.train_and_evaluate(features, y, model_name)
        results[encoder_name] = result.test_metrics

    # Print comparison
    print()
    print("=" * 88)
    print("ENCODER ABLATION — TEST METRICS FOR MODEL A")
    print("=" * 88)
    header = f"{'Encoder':<40}" + "".join(f"{m.upper():>10}" for m in ["MAE", "MdAE", "PRED25", "R2", "SA"])
    print(header)
    print("-" * 88)
    for enc, metrics in results.items():
        row = f"{enc:<40}"
        row += f"{metrics.get('mae', 0):>10.1f}"
        row += f"{metrics.get('mdae', 0):>10.1f}"
        row += f"{metrics.get('pred_25', 0):>10.2f}"
        row += f"{metrics.get('r2', 0):>10.4f}"
        row += f"{metrics.get('sa', 0):>10.2f}"
        print(row)
    print()

    # Save
    out_path = get_model_dir() / "encoder_ablation.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Ablation results saved to {out_path}")
    logger.info(f"Total time: {(_time.time() - start)/60:.1f} min")


def step_sensitivity(config: dict):
    """Sensitivity analysis: train Models A, B, C at multiple duration thresholds.

    Tests robustness of findings across different max_duration_days caps.
    Prints a comparison table and runs Wilcoxon tests at each threshold
    to see whether the A vs C significance conclusion changes.
    """
    import copy
    import time as _time
    from scipy import stats
    from src.modeling.trainer import ModelTrainer

    thresholds_days = [14, 30, 60, 90, None]  # None = no cap
    start = _time.time()

    df_full = _load_raw_data()
    min_hours = config["filtering"]["min_duration_hours"]

    # We need NLP and repo features for all models
    nlp_all = _load_features("nlp_features")
    try:
        repo_all = _load_features("repo_features")
        has_repo = True
    except FileNotFoundError:
        repo_all = None
        has_repo = False
        logger.warning("Repo features not found — will only run Model A sensitivity")

    logger.info(f"{'='*90}")
    logger.info(f"SENSITIVITY ANALYSIS — {len(thresholds_days)} duration thresholds")
    logger.info(f"{'='*90}")

    rows = []

    for cap_days in thresholds_days:
        cap_label = f"{cap_days}d" if cap_days else "no cap"
        max_hours = cap_days * 24 if cap_days else float("inf")

        # Apply filter
        mask = (df_full["duration_hours"] >= min_hours)
        if cap_days:
            mask = mask & (df_full["duration_hours"] <= max_hours)
        df = df_full[mask].reset_index(drop=True)
        nlp = nlp_all[mask].reset_index(drop=True)
        y = df["duration_hours"]

        n = len(df)
        logger.info(f"\n--- Threshold: {cap_label} ({n} samples) ---")

        if n < 50:
            logger.warning(f"  Too few samples ({n}), skipping")
            continue

        cfg = copy.deepcopy(config)
        trainer = ModelTrainer(cfg)

        # Model A
        result_a = trainer.train_and_evaluate(nlp, y, f"sensitivity_a_{cap_label}")
        row = {
            "threshold": cap_label,
            "n_samples": n,
            "a_mae": result_a.test_metrics["mae"],
            "a_mdae": result_a.test_metrics["mdae"],
            "a_sa": result_a.test_metrics["sa"],
            "a_r2": result_a.test_metrics["r2"],
            "a_pred25": result_a.test_metrics["pred_25"],
        }

        if has_repo:
            repo = repo_all[mask].reset_index(drop=True)

            # Model B
            result_b = trainer.train_and_evaluate(repo, y, f"sensitivity_b_{cap_label}")
            row["b_mae"] = result_b.test_metrics["mae"]
            row["b_sa"] = result_b.test_metrics["sa"]
            row["b_r2"] = result_b.test_metrics["r2"]

            # Model C
            combined = pd.concat([nlp, repo], axis=1)
            result_c = trainer.train_and_evaluate(combined, y, f"sensitivity_c_{cap_label}")
            row["c_mae"] = result_c.test_metrics["mae"]
            row["c_sa"] = result_c.test_metrics["sa"]
            row["c_r2"] = result_c.test_metrics["r2"]
            row["c_pred25"] = result_c.test_metrics["pred_25"]

            # Wilcoxon A vs C
            errors_a = np.abs(result_a.test_actuals - result_a.test_predictions)
            errors_c = np.abs(result_c.test_actuals - result_c.test_predictions)
            try:
                _, p_ac = stats.wilcoxon(errors_a, errors_c)
                row["a_vs_c_p"] = p_ac
                row["a_vs_c_sig"] = "YES" if p_ac < 0.05 else "no"
            except Exception:
                row["a_vs_c_p"] = None
                row["a_vs_c_sig"] = "err"

            # Wilcoxon A vs B
            errors_b = np.abs(result_b.test_actuals - result_b.test_predictions)
            try:
                _, p_ab = stats.wilcoxon(errors_a, errors_b)
                row["a_vs_b_p"] = p_ab
                row["a_vs_b_sig"] = "YES" if p_ab < 0.05 else "no"
            except Exception:
                row["a_vs_b_p"] = None
                row["a_vs_b_sig"] = "err"

        rows.append(row)

    # Print summary table
    print()
    print("=" * 100)
    print("SENSITIVITY ANALYSIS RESULTS")
    print("=" * 100)

    if has_repo:
        header = (f"{'Threshold':<10} {'N':>6}  "
                  f"{'A MAE':>8} {'A SA':>7} {'A P25':>7}  "
                  f"{'B MAE':>8} {'B SA':>7}  "
                  f"{'C MAE':>8} {'C SA':>7} {'C P25':>7}  "
                  f"{'A=C p':>10} {'Sig?':>5}")
        print(header)
        print("-" * 100)
        for r in rows:
            p_val = r.get("a_vs_c_p")
            p_str = f"{p_val:.6f}" if p_val is not None else "—"
            print(f"{r['threshold']:<10} {r['n_samples']:>6}  "
                  f"{r['a_mae']:>8.1f} {r['a_sa']:>6.1f}% {r['a_pred25']:>6.1f}%  "
                  f"{r.get('b_mae', 0):>8.1f} {r.get('b_sa', 0):>6.1f}%  "
                  f"{r.get('c_mae', 0):>8.1f} {r.get('c_sa', 0):>6.1f}% {r.get('c_pred25', 0):>6.1f}%  "
                  f"{p_str:>10} {r.get('a_vs_c_sig', '—'):>5}")
    else:
        header = f"{'Threshold':<10} {'N':>6}  {'A MAE':>8} {'A SA':>7} {'A P25':>7} {'A R2':>8}"
        print(header)
        print("-" * 60)
        for r in rows:
            print(f"{r['threshold']:<10} {r['n_samples']:>6}  "
                  f"{r['a_mae']:>8.1f} {r['a_sa']:>6.1f}% {r['a_pred25']:>6.1f}% {r['a_r2']:>8.4f}")

    print()

    # Interpretation
    if has_repo:
        sig_count = sum(1 for r in rows if r.get("a_vs_c_sig") == "YES")
        total = len([r for r in rows if "a_vs_c_sig" in r])
        print(f"A vs C significant at {sig_count}/{total} thresholds")
        if sig_count == 0:
            print("=> NULL RESULT IS ROBUST: combining features never significantly helps")
        elif sig_count == total:
            print("=> COMBINATION HELPS at all thresholds")
        else:
            print("=> MIXED: result depends on threshold choice (report as boundary condition)")

    # Save
    results_df = pd.DataFrame(rows)
    out_path = get_model_dir() / "sensitivity_analysis.csv"
    results_df.to_csv(out_path, index=False)
    logger.info(f"Sensitivity table saved to {out_path}")

    elapsed = _time.time() - start
    logger.info(f"Sensitivity analysis complete in {elapsed/60:.1f} min")


def step_error_analysis(config: dict):
    """Step 6: Error analysis — scatter plots, bucket grids, SHAP importance.

    Per trained model, produces:
      - actual_vs_predicted.png       (scatter with ±25% bands)
      - bucket_grid.png               (classification-style confusion grid)
      - error_by_range.png            (error box plot by duration bucket)
      - feature_importance.png        (XGBoost top features)
    Saved to models/<name>/analysis/
    """
    from src.analysis.error_analysis import run_error_analysis
    run_error_analysis(model_key=None)  # all models


def step_examples(config: dict):
    """Step 7: Extract representative good/bad predictions per bucket.

    For each model, samples the best and worst predictions in each
    duration bucket and writes them as a readable markdown report.
    Useful for qualitative error analysis in the paper.
    """
    from src.analysis.example_predictions import run_extract_examples
    run_extract_examples(n_per_bucket=3)


def step_analyze(config: dict):
    """Step 5: Statistical comparison between trained models.

    Loads predictions.csv from each model directory, runs Wilcoxon
    signed-rank tests and Cliff's delta on test-set errors, and prints
    a formatted report. Also loads results.json if available.
    """
    from scipy import stats

    model_dir = get_model_dir()

    # Load per-model predictions
    preds = {}
    test_metrics = {}
    for key, subdir in [("A", "model_a_text_only"),
                        ("B", "model_b_repo_only"),
                        ("C", "model_c_combined")]:
        preds_path = model_dir / subdir / "predictions.csv"
        results_path = model_dir / subdir / "results.json"

        if not preds_path.exists():
            logger.warning(f"Model {key}: predictions.csv not found at {preds_path}")
            continue

        df = pd.read_csv(preds_path)
        test_df = df[df["split"] == "test"].reset_index(drop=True)
        errors = (test_df["actual_hours"] - test_df["predicted_hours"]).abs().values
        preds[key] = {"df": test_df, "errors": errors}

        if results_path.exists():
            with open(results_path) as f:
                test_metrics[key] = json.load(f).get("test_metrics", {})

    if len(preds) < 2:
        logger.warning("Need at least 2 models trained to run comparison")
        return

    # Print summary metrics
    print()
    print("=" * 72)
    print("MODEL PERFORMANCE SUMMARY (test set)")
    print("=" * 72)
    print(f"{'Metric':<12} {'Model A':>12} {'Model B':>12} {'Model C':>12}")
    print("-" * 72)
    for metric in ["mae", "mdae", "mre", "pred_25", "pred_50", "r2", "sa"]:
        label = {
            "mae": "MAE (h)",
            "mdae": "MdAE (h)",
            "mre": "MMRE",
            "pred_25": "PRED(25) %",
            "pred_50": "PRED(50) %",
            "r2": "R²",
            "sa": "SA %",
        }[metric]
        row = f"{label:<12}"
        for key in ["A", "B", "C"]:
            if key in test_metrics and metric in test_metrics[key]:
                val = test_metrics[key][metric]
                if metric in ["r2"]:
                    row += f" {val:>12.4f}"
                elif metric == "mre":
                    row += f" {val:>11.2%}"
                else:
                    row += f" {val:>12.2f}"
            else:
                row += f" {'—':>12}"
        print(row)
    print()

    # Pairwise statistical tests
    print("=" * 72)
    print("PAIRWISE STATISTICAL COMPARISON")
    print("=" * 72)
    print("Null hypothesis: absolute errors between models come from the same distribution")
    print(f"Significance level α = {config['statistics']['wilcoxon_alpha']}")
    print()

    pairs = [("A", "B"), ("A", "C"), ("B", "C")]
    alpha = config["statistics"]["wilcoxon_alpha"]
    thresholds = config["statistics"]["cliff_delta_thresholds"]

    for k1, k2 in pairs:
        if k1 not in preds or k2 not in preds:
            continue

        e1 = preds[k1]["errors"]
        e2 = preds[k2]["errors"]

        if len(e1) != len(e2):
            print(f"Model {k1} vs {k2}: SKIP (different test set sizes: {len(e1)} vs {len(e2)})")
            continue

        # Wilcoxon signed-rank test
        try:
            stat, p_value = stats.wilcoxon(e1, e2)
        except ValueError as e:
            print(f"Model {k1} vs {k2}: Wilcoxon failed ({e})")
            continue

        # Cliff's delta
        more = int(np.sum(e1[:, None] > e2[None, :]))
        less = int(np.sum(e1[:, None] < e2[None, :]))
        delta = (more - less) / (len(e1) * len(e2))
        abs_delta = abs(delta)
        if abs_delta < thresholds["negligible"]:
            effect = "negligible"
        elif abs_delta < thresholds["small"]:
            effect = "small"
        elif abs_delta < thresholds["medium"]:
            effect = "medium"
        else:
            effect = "large"

        # Which model has lower errors (better)
        mean_e1, mean_e2 = e1.mean(), e2.mean()
        if mean_e1 < mean_e2:
            better = f"Model {k1}"
            improvement = (mean_e2 - mean_e1) / mean_e2 * 100
        else:
            better = f"Model {k2}"
            improvement = (mean_e1 - mean_e2) / mean_e1 * 100

        sig = "✓ SIGNIFICANT" if p_value < alpha else "✗ not significant"

        print(f"Model {k1} vs Model {k2}:")
        print(f"  Wilcoxon statistic: {stat:.1f}")
        print(f"  p-value:            {p_value:.6f}  ({sig} at α={alpha})")
        print(f"  Cliff's delta:      {delta:+.4f}  (effect size: {effect})")
        print(f"  Better model:       {better} (mean error {improvement:.1f}% lower)")
        print()

    print("=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    print("Wilcoxon p < α: the two models' error distributions differ significantly")
    print("Cliff's delta (unbiased effect size):")
    print(f"  |δ| < {thresholds['negligible']:.3f}: negligible")
    print(f"  |δ| < {thresholds['small']:.3f}: small")
    print(f"  |δ| < {thresholds['medium']:.3f}: medium")
    print(f"  |δ| ≥ {thresholds['medium']:.3f}: large")
    print()

    # Save full report
    summary = {
        "test_metrics": test_metrics,
        "comparisons": {},
    }
    for k1, k2 in pairs:
        if k1 not in preds or k2 not in preds:
            continue
        e1, e2 = preds[k1]["errors"], preds[k2]["errors"]
        if len(e1) != len(e2):
            continue
        try:
            stat, p = stats.wilcoxon(e1, e2)
            more = int(np.sum(e1[:, None] > e2[None, :]))
            less = int(np.sum(e1[:, None] < e2[None, :]))
            delta = (more - less) / (len(e1) * len(e2))
            summary["comparisons"][f"{k1}_vs_{k2}"] = {
                "wilcoxon_stat": float(stat),
                "p_value": float(p),
                "significant": bool(p < alpha),
                "cliffs_delta": float(delta),
                "mean_abs_error_1": float(e1.mean()),
                "mean_abs_error_2": float(e2.mean()),
            }
        except Exception:
            continue

    out_path = model_dir / "analysis_report.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Analysis report saved to {out_path}")


def step_shap_analysis(config: dict):
    """Step: SHAP value analysis for trained models.

    Computes per-feature SHAP values using TreeExplainer and generates:
    - shap_summary.png (beeswarm plot — direction + magnitude)
    - shap_bar.png (mean |SHAP| bar chart)
    - shap_values.csv (mean absolute SHAP per feature)
    """
    from src.analysis.shap_analysis import run_shap_analysis
    run_shap_analysis(model_key=None)


def main():
    parser = argparse.ArgumentParser(description="SE3M Replication Study Pipeline")
    parser.add_argument(
        "--step",
        choices=["validate", "collect", "merge_data", "clean_data", "data_quality",
                 "features", "nlp_features",
                 "repo_features", "train_model_a", "train_model_b_no_numfiles",
                 "train", "analyze",
                 "error_analysis", "shap_analysis", "examples", "sensitivity",
                 "encoder_ablation", "feature_selection_ablation",
                 "dimensionality_sweep", "all"],
        required=True,
        help="Pipeline step to run",
    )
    parser.add_argument("--config", default=None, help="Path to config YAML")
    parser.add_argument(
        "--merge-from",
        default=None,
        help="Path to partner's parquet/csv file (for merge_data step)",
    )
    parser.add_argument(
        "--encoder",
        default=None,
        help=(
            "Override nlp.model_name to swap encoders. Examples: "
            "microsoft/codebert-base (default), microsoft/unixcoder-base, "
            "microsoft/graphcodebert-base, BAAI/bge-base-en-v1.5, "
            "intfloat/e5-base-v2, sentence-transformers/all-mpnet-base-v2"
        ),
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.encoder:
        config.setdefault("nlp", {})
        config["nlp"]["model_name"] = args.encoder
        logger.info(f"Encoder override: {args.encoder}")

    steps = {
        "validate": step_validate,
        "collect": step_collect,
        "merge_data": lambda c: step_merge_data(c, merge_path=args.merge_from),
        "clean_data": step_clean_data,
        "data_quality": lambda c: __import__("src.analysis.data_quality", fromlist=["run_data_quality_report"]).run_data_quality_report(),
        "features": step_features,
        "nlp_features": step_nlp_features,
        "repo_features": step_repo_features,
        "train_model_a": step_train_model_a,
        "train_model_b_no_numfiles": step_train_model_b_no_numfiles,
        "train": step_train,
        "analyze": step_analyze,
        "error_analysis": step_error_analysis,
        "shap_analysis": step_shap_analysis,
        "examples": step_examples,
        "sensitivity": step_sensitivity,
        "encoder_ablation": step_encoder_ablation,
        "feature_selection_ablation": step_feature_selection_ablation,
        "dimensionality_sweep": step_dimensionality_sweep,
    }

    if args.step == "all":
        for name, func in steps.items():
            if name == "merge_data":
                continue
            logger.info(f"\n{'='*60}\nRunning step: {name}\n{'='*60}")
            func(config)
    else:
        steps[args.step](config)


if __name__ == "__main__":
    main()
