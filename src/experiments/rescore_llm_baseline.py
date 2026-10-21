"""Re-score an existing LLM zero-shot run against the paper's current test split.

Background
----------
``llm_baseline.py`` scores SA against a mean-predictor baseline and, in its
first version, read Model A's test rows from results.json indices that were
plain 0..n-1 ranges (index lost in the trainer's embedding reduction, since
fixed).  The paper scores SA against a 1,000-run random-guess baseline
(Shepperd & MacDonell, 2012) on an 865-row test split.  This script takes
whatever the LLM has predicted (any mix of runs, merged via the script's
resume file), keeps only the issues in the verified test split, and re-scores
them exactly as the trainer does.

What this script does
---------------------
1. Loads the April gpt-4o predictions (repo, issue_number, predicted_hours).
2. Rebuilds the current Model A test/train split from
   ``models/model_a_text_only/results.json`` (stored indices), and verifies it
   equals ``train_test_split(test_size, random_state)`` from the config.
3. Inner-joins the LLM predictions to the current test issues on
   repo + issue_number and replaces the actual durations with the current
   cleaned values.
4. Recomputes every metric with the same logic as
   ``src/modeling/trainer.py`` (``compute_metrics`` / ``_compute_sa``):
   1,000 random-guess runs, seeded, sampling the *training* actuals with
   replacement.
5. Writes ``models/llm_baseline/<model>/results.json`` in the same schema as
   ``models/model_a_text_only/results.json`` and overwrites
   ``predictions.csv`` with only the matched rows.  The original 896-row run
   is preserved in ``partial_results.json``.

Usage:
    python src/experiments/rescore_llm_baseline.py                 # gpt-4o
    python src/experiments/rescore_llm_baseline.py --model gpt-4o --dry-run
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.utils.config import load_config  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Same duration filter the training pipeline applies (1 hour to 90 days).
DURATION_MIN_H = 1
DURATION_MAX_H = 2160
N_RUNS = 1000


# ---------------------------------------------------------------------------
# Metric functions: verbatim logic from src/modeling/trainer.py
# ---------------------------------------------------------------------------
def compute_sa(model_errors: np.ndarray, test_actuals: np.ndarray,
               train_actuals: np.ndarray, seed: int, n_runs: int = N_RUNS) -> dict:
    """Mirror of ModelTrainer._compute_sa (1,000-run random baseline)."""
    rng = np.random.RandomState(seed)
    n_test = len(test_actuals)
    model_mae = float(np.mean(model_errors))

    random_maes = []
    for _ in range(n_runs):
        random_preds = rng.choice(train_actuals, size=n_test, replace=True)
        random_errors = np.abs(test_actuals - random_preds)
        random_maes.append(float(np.mean(random_errors)))

    mean_random_mae = float(np.mean(random_maes))
    std_random_mae = float(np.std(random_maes, ddof=1))

    if mean_random_mae == 0:
        return {"sa": 0.0, "mae_p0": 0.0, "std_p0": 0.0, "glass_delta": 0.0}

    sa = (1 - model_mae / mean_random_mae) * 100
    glass_delta = ((mean_random_mae - model_mae) / std_random_mae
                   if std_random_mae > 0 else 0.0)
    return {
        "sa": float(sa),
        "mae_p0": float(mean_random_mae),
        "std_p0": float(std_random_mae),
        "glass_delta": float(glass_delta),
    }


def compute_metrics(actuals: np.ndarray, predictions: np.ndarray,
                    train_actuals: np.ndarray, seed: int) -> dict:
    """Mirror of ModelTrainer.compute_metrics."""
    errors = np.abs(actuals - predictions)
    relative_errors = errors / np.maximum(actuals, 1e-6)
    sa_result = compute_sa(errors, actuals, train_actuals, seed)
    return {
        "mae": float(np.mean(errors)),
        "mdae": float(np.median(errors)),
        "mre": float(np.mean(relative_errors)),
        "pred_25": float(np.mean(relative_errors <= 0.25) * 100),
        "pred_50": float(np.mean(relative_errors <= 0.50) * 100),
        "r2": float(1 - np.sum((actuals - predictions) ** 2)
                    / np.sum((actuals - np.mean(actuals)) ** 2)),
        "sa": sa_result["sa"],
        "mae_p0": sa_result["mae_p0"],
        "std_p0": sa_result["std_p0"],
        "glass_delta": sa_result["glass_delta"],
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_filtered_raw() -> pd.DataFrame:
    parquet_path = ROOT / "data" / "raw" / "issue_pr_pairs.parquet"
    csv_path = ROOT / "data" / "raw" / "issue_pr_pairs.csv"
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        raise FileNotFoundError("data/raw/issue_pr_pairs.{parquet,csv} not found")
    mask = (df["duration_hours"] >= DURATION_MIN_H) & (df["duration_hours"] <= DURATION_MAX_H)
    df = df[mask].reset_index(drop=True)
    df["issue_number"] = df["issue_number"].astype(int)
    return df


def load_model_a_split(df: pd.DataFrame, seed: int, test_size: float):
    """Return (train_indices, test_indices) and verify they match a fresh split."""
    results_path = ROOT / "models" / "model_a_text_only" / "results.json"
    with open(results_path) as f:
        model_a = json.load(f)
    train_idx = np.asarray(model_a["train_indices"], dtype=int)
    test_idx = np.asarray(model_a["test_indices"], dtype=int)

    # Reproduce the trainer's split on the same filtered frame.  This is the
    # ground truth: ModelTrainer.reduce_embeddings() calls reset_index() on
    # the already-split frames, so for any model with embedding reduction
    # (A, C, sensitivity_a/c, ...) the stored train/test_indices are just
    # 0..n_train-1 and 0..n_test-1, not positions in the data.  Model B has
    # no embeddings and stores correct indices.
    fresh_train, fresh_test = train_test_split(
        np.arange(len(df)), test_size=test_size, random_state=seed
    )
    if np.array_equal(fresh_train, train_idx) and np.array_equal(fresh_test, test_idx):
        logger.info("Stored Model A indices match the fresh split")
    else:
        positional = (np.array_equal(train_idx, np.arange(len(train_idx)))
                      and np.array_equal(test_idx, np.arange(len(test_idx))))
        logger.warning(
            "Stored Model A train/test_indices do NOT match train_test_split("
            f"test_size={test_size}, random_state={seed}); "
            + ("they are plain 0..n ranges (index lost in reduce_embeddings). "
               if positional else "")
            + "Using the reproduced split instead."
        )
        train_idx, test_idx = fresh_train, fresh_test

    # Hard check: the actuals at the chosen test positions must equal the
    # test actuals Model A was scored on (predictions.csv, in split order).
    preds_path = ROOT / "models" / "model_a_text_only" / "predictions.csv"
    preds = pd.read_csv(preds_path)
    test_actuals_csv = preds.loc[preds["split"] == "test", "actual_hours"].to_numpy()
    train_actuals_csv = preds.loc[preds["split"] == "train", "actual_hours"].to_numpy()
    if (len(test_actuals_csv) != len(test_idx)
            or not np.allclose(test_actuals_csv, df.iloc[test_idx]["duration_hours"].to_numpy())
            or not np.allclose(train_actuals_csv, df.iloc[train_idx]["duration_hours"].to_numpy())):
        raise RuntimeError(
            "Rebuilt split does not reproduce the actuals in "
            "models/model_a_text_only/predictions.csv; cannot identify the test issues."
        )
    logger.info(f"Model A split verified against predictions.csv: {len(train_idx)} train / "
                f"{len(test_idx)} test (seed={seed}, test_size={test_size}, filtered rows={len(df)})")

    return train_idx, test_idx, model_a


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Re-score an LLM baseline run on the current test split")
    parser.add_argument("--model", default="gpt-4o", help="LLM run to re-score (folder under models/llm_baseline)")
    parser.add_argument("--dry-run", action="store_true", help="Print metrics but do not write files")
    args = parser.parse_args()

    config = load_config()
    model_cfg = config["modeling"]
    seed = model_cfg["random_seed"]
    test_size = model_cfg["test_size"]

    model_slug = args.model.replace("/", "_").replace(".", "_")
    out_dir = ROOT / "models" / "llm_baseline" / model_slug
    llm_preds_path = out_dir / "predictions.csv"
    if not llm_preds_path.exists():
        raise FileNotFoundError(f"{llm_preds_path} not found; run llm_baseline.py first")

    # 1. Original LLM run
    llm = pd.read_csv(llm_preds_path)
    llm["issue_number"] = llm["issue_number"].astype(int)
    llm = llm.dropna(subset=["predicted_hours"])
    logger.info(f"Loaded {len(llm)} {args.model} predictions from {llm_preds_path}")

    # 2. Current data and Model A split
    df = load_filtered_raw()
    train_idx, test_idx, model_a = load_model_a_split(df, seed, test_size)
    train_actuals = df.iloc[train_idx]["duration_hours"].to_numpy()
    test_df = df.iloc[test_idx][["repo", "issue_number", "duration_hours"]].rename(
        columns={"duration_hours": "actual_hours_current"}
    )

    # 3. Inner join on repo + issue_number
    matched = test_df.merge(llm, on=["repo", "issue_number"], how="inner", validate="one_to_one")
    n_expected = len(test_idx)
    print()
    print("=" * 70)
    print(f"MATCHING: {len(matched)} of {n_expected} current test issues found in the {args.model} run")
    if len(matched) < n_expected:
        missing = test_df.merge(llm[["repo", "issue_number"]], on=["repo", "issue_number"],
                                how="left", indicator=True)
        missing = missing[missing["_merge"] == "left_only"]
        print(f"  WARNING: {len(missing)} current test issues have no LLM prediction:")
        for _, r in missing.head(20).iterrows():
            print(f"    {r['repo']}#{r['issue_number']}")
    print("=" * 70)

    # 4. Replace actuals with the cleaned values and report what changed
    matched = matched.rename(columns={"actual_hours": "actual_hours_original"})
    matched["actual_hours"] = matched["actual_hours_current"]
    matched = matched.drop(columns=["actual_hours_current"])
    delta = (matched["actual_hours"] - matched["actual_hours_original"]).abs()
    n_changed = int((delta > 1e-6).sum())
    n_changed_1h = int((delta > 1).sum())
    print(f"Actual durations changed by dataset cleaning: {n_changed} rows "
          f"({n_changed_1h} by more than 1h)")
    top = matched.loc[delta.sort_values(ascending=False).index[:5],
                      ["repo", "issue_number", "actual_hours_original", "actual_hours"]]
    print("Largest changes (for Threats to Validity):")
    for _, r in top.iterrows():
        print(f"  {r['repo']}#{r['issue_number']}: "
              f"{r['actual_hours_original']:.1f}h -> {r['actual_hours']:.1f}h "
              f"(delta {abs(r['actual_hours'] - r['actual_hours_original']):.1f}h)")

    # 5. Metrics with the paper's 1,000-run random baseline
    actuals = matched["actual_hours"].to_numpy(dtype=float)
    predictions = matched["predicted_hours"].to_numpy(dtype=float)
    metrics = compute_metrics(actuals, predictions, train_actuals, seed)
    model_a_metrics = model_a["test_metrics"]

    print()
    print("=" * 70)
    print(f"RE-SCORED {args.model} ZERO-SHOT vs MODEL A  (n={len(matched)}, "
          f"{N_RUNS}-run random baseline from {len(train_actuals)} training actuals)")
    print("=" * 70)
    print(f"  {'Metric':<12} {'LLM':>12} {'Model A':>12}")
    for label, key in [("MAE", "mae"), ("MdAE", "mdae"), ("MRE", "mre"), ("PRED(25)", "pred_25"),
                       ("PRED(50)", "pred_50"), ("R2", "r2"), ("SA", "sa"), ("MAE_P0", "mae_p0"),
                       ("STD_P0", "std_p0"), ("Glass delta", "glass_delta")]:
        print(f"  {label:<12} {metrics[key]:>12.3f} {model_a_metrics.get(key, float('nan')):>12.3f}")
    print()

    if args.dry_run:
        logger.info("Dry run: no files written")
        return

    # 6. Write results.json in the Model A schema
    results = {
        "name": f"llm_baseline_{model_slug}",
        "train_metrics": None,  # zero-shot: no training on this data
        "test_metrics": metrics,
        "best_params": {
            "llm_model": args.model,
            "temperature": 0.0,
            "max_output_tokens": 200,
            "prompting": "zero-shot, issue title + body truncated to 2000 chars",
        },
        "feature_names": ["issue_title", "issue_body"],
        "n_features": 2,
        "n_train": int(len(train_idx)),
        "n_test": int(len(matched)),
        "train_indices": [int(i) for i in train_idx],
        "test_indices": [int(i) for i in test_idx],
        "rescoring": {
            "source_run": ("llm_baseline.py: 192 predictions from the 2026-04-21 run (which scored "
                           "the first 896 dataset rows due to the stored-index bug) plus 673 new "
                           "predictions on 2026-10-21 for the remaining verified test issues"),
            "rescored_on": date.today().isoformat(),
            "n_source_predictions": int(len(llm)),
            "n_matched": int(len(matched)),
            "n_actuals_changed_by_cleaning": n_changed,
            "n_actuals_changed_more_than_1h": n_changed_1h,
            "sa_baseline": f"{N_RUNS}-run random guessing sampled from training actuals, seed {seed}",
            "model_a_results": "models/model_a_text_only/results.json",
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    # 7. Overwrite predictions.csv with the matched rows only
    cols = ["repo", "issue_number", "issue_title", "actual_hours", "actual_hours_original",
            "predicted_hours", "reasoning"]
    matched[cols].to_csv(llm_preds_path, index=False)
    logger.info(f"Wrote {out_dir / 'results.json'} and {llm_preds_path} ({len(matched)} rows)")


if __name__ == "__main__":
    main()
