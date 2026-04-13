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


def step_nlp_features(config: dict):
    """Step 3a: Extract NLP features (CodeBERT embeddings + derived)."""
    import time as _time
    from src.feature_extraction.nlp_features import NLPFeatureExtractor

    start = _time.time()
    data_dir = get_data_dir()
    df = _load_raw_data()

    logger.info(f"{'='*60}")
    logger.info(f"Extracting NLP features for {len(df)} issue-PR pairs")
    logger.info(f"{'='*60}")

    nlp_extractor = NLPFeatureExtractor(config)
    nlp_features = nlp_extractor.extract_all_features(df)

    out_path = data_dir / "processed" / "nlp_features.parquet"
    _save_features(nlp_features, out_path)

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

    for repo in config["repositories"]:
        repo_path = cloner.clone_or_update(repo["owner"], repo["name"])
        repo_df = df[df["repo"] == f"{repo['owner']}/{repo['name']}"]

        if len(repo_df) == 0:
            logger.info(f"  No pairs for {repo['owner']}/{repo['name']}, skipping")
            continue

        logger.info(f"  Extracting features for {len(repo_df)} pairs from {repo['owner']}/{repo['name']}...")
        extractor = RepoFeatureExtractor(repo_path, config)
        features = extractor.extract_all_features(repo_df)
        all_repo_features.append(features)

    repo_features = pd.concat(all_repo_features)

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


def step_train(config: dict):
    """Step 4: Train Models A, B, C and compare."""
    from src.modeling.trainer import ModelTrainer

    df = _load_raw_data()
    nlp_features = _load_features("nlp_features")

    # Apply duration filter to all models consistently
    max_hours = config["filtering"]["max_duration_days"] * 24
    min_hours = config["filtering"]["min_duration_hours"]
    mask = (df["duration_hours"] >= min_hours) & (df["duration_hours"] <= max_hours)
    n_before = len(df)
    df = df[mask].reset_index(drop=True)
    nlp_features = nlp_features[mask].reset_index(drop=True)
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
        repo_features = repo_features[mask].reset_index(drop=True)
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


def step_analyze(config: dict):
    """Step 5: SHAP analysis and error analysis."""
    from src.analysis.shap_analysis import SHAPAnalyzer

    logger.info("Running SHAP and error analysis (requires trained models)")
    logger.info("This step will be fully implemented after training completes")


def main():
    parser = argparse.ArgumentParser(description="SE3M Replication Study Pipeline")
    parser.add_argument(
        "--step",
        choices=["validate", "collect", "merge_data", "features", "nlp_features",
                 "repo_features", "train_model_a", "train", "analyze", "all"],
        required=True,
        help="Pipeline step to run",
    )
    parser.add_argument("--config", default=None, help="Path to config YAML")
    parser.add_argument(
        "--merge-from",
        default=None,
        help="Path to partner's parquet/csv file (for merge_data step)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    steps = {
        "validate": step_validate,
        "collect": step_collect,
        "merge_data": lambda c: step_merge_data(c, merge_path=args.merge_from),
        "features": step_features,
        "nlp_features": step_nlp_features,
        "repo_features": step_repo_features,
        "train_model_a": step_train_model_a,
        "train": step_train,
        "analyze": step_analyze,
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
