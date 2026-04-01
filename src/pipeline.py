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

    # Only collect from repos that passed validation
    validation_path = get_data_dir() / "repo_validation.json"
    valid_repos = set()
    if validation_path.exists():
        import json
        with open(validation_path) as f:
            for r in json.load(f):
                if r.get("passes_all"):
                    valid_repos.add(r["repo"])

    for repo in config["repositories"]:
        repo_full = f"{repo['owner']}/{repo['name']}"
        if valid_repos and repo_full not in valid_repos:
            logger.info(f"Skipping {repo_full} (did not pass validation)")
            continue

        pairs = miner.mine_issue_pr_pairs(
            repo["owner"], repo["name"], save_path=out_path
        )
        all_pairs.extend(pairs)

    df = miner.pairs_to_dataframe(all_pairs)

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


def step_train(config: dict):
    """Step 4: Train Models A, B, C and compare."""
    from src.modeling.trainer import ModelTrainer

    data_dir = get_data_dir()
    df = pd.read_parquet(data_dir / "raw" / "issue_pr_pairs.parquet")
    nlp_features = pd.read_parquet(data_dir / "processed" / "nlp_features.parquet")
    repo_features = pd.read_parquet(data_dir / "processed" / "repo_features.parquet")

    y = df["duration_hours"]
    trainer = ModelTrainer(config)

    # Model A: Text-only
    result_a = trainer.train_and_evaluate(nlp_features, y, "model_a_text_only")

    # Model B: Repo-only
    result_b = trainer.train_and_evaluate(repo_features, y, "model_b_repo_only")

    # Model C: Combined
    combined = pd.concat([nlp_features, repo_features], axis=1)
    result_c = trainer.train_and_evaluate(combined, y, "model_c_combined")

    # Statistical comparison
    comparisons = trainer.compare_models(result_a, result_b, result_c)

    # Save results
    results = {
        "model_a": result_a.cv_scores,
        "model_b": result_b.cv_scores,
        "model_c": result_c.cv_scores,
        "comparisons": comparisons,
    }

    out_path = get_model_dir() / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {out_path}")
    return result_a, result_b, result_c, comparisons


def step_analyze(config: dict):
    """Step 5: SHAP analysis and error analysis."""
    from src.analysis.shap_analysis import SHAPAnalyzer

    logger.info("Running SHAP and error analysis (requires trained models)")
    logger.info("This step will be fully implemented after training completes")


def main():
    parser = argparse.ArgumentParser(description="SE3M Replication Study Pipeline")
    parser.add_argument(
        "--step",
        choices=["validate", "collect", "features", "nlp_features", "repo_features", "train", "analyze", "all"],
        required=True,
        help="Pipeline step to run",
    )
    parser.add_argument("--config", default=None, help="Path to config YAML")
    args = parser.parse_args()

    config = load_config(args.config)

    steps = {
        "validate": step_validate,
        "collect": step_collect,
        "features": step_features,
        "nlp_features": step_nlp_features,
        "repo_features": step_repo_features,
        "train": step_train,
        "analyze": step_analyze,
    }

    if args.step == "all":
        for name, func in steps.items():
            logger.info(f"\n{'='*60}\nRunning step: {name}\n{'='*60}")
            func(config)
    else:
        steps[args.step](config)


if __name__ == "__main__":
    main()
