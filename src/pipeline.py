"""Main pipeline orchestrating the full SE3M replication study.

Usage:
    python -m src.pipeline --step validate    # Step 1: Validate target repos
    python -m src.pipeline --step collect     # Step 2: Mine issue-PR pairs
    python -m src.pipeline --step features    # Step 3: Extract all features
    python -m src.pipeline --step train       # Step 4: Train and evaluate models
    python -m src.pipeline --step analyze     # Step 5: SHAP + error analysis
    python -m src.pipeline --step all         # Run full pipeline
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
            print(f"Skipping {repo_full} (did not pass validation)")
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
        print("  (Saved as CSV — install pyarrow for parquet support)")

    print(f"\n{'='*60}")
    print(f"Collection complete: {len(df)} total issue-PR pairs")
    print(f"Saved to {saved_path}")
    print(f"{'='*60}")
    if len(df) > 0:
        logger.info(f"Duration stats:\n{df['duration_hours'].describe()}")
    return df


def step_features(config: dict):
    """Step 3: Extract NLP and repository features."""
    from src.data_collection.repo_cloner import RepoCloner
    from src.feature_extraction.nlp_features import NLPFeatureExtractor
    from src.feature_extraction.repo_features import RepoFeatureExtractor

    data_dir = get_data_dir()
    df = pd.read_parquet(data_dir / "raw" / "issue_pr_pairs.parquet")

    # NLP features
    nlp_extractor = NLPFeatureExtractor(config)
    nlp_features = nlp_extractor.extract_all_features(df)
    nlp_features.to_parquet(data_dir / "processed" / "nlp_features.parquet")
    logger.info(f"NLP features: {nlp_features.shape}")

    # Repository features (per-repo)
    cloner = RepoCloner()
    all_repo_features = []

    for repo in config["repositories"]:
        repo_path = cloner.clone_or_update(repo["owner"], repo["name"])
        repo_df = df[df["repo"] == f"{repo['owner']}/{repo['name']}"]

        if len(repo_df) == 0:
            continue

        extractor = RepoFeatureExtractor(repo_path, config)
        features = extractor.extract_all_features(repo_df)
        all_repo_features.append(features)

    repo_features = pd.concat(all_repo_features)
    repo_features.to_parquet(data_dir / "processed" / "repo_features.parquet")
    logger.info(f"Repo features: {repo_features.shape}")

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
        choices=["validate", "collect", "features", "train", "analyze", "all"],
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
