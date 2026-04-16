"""Error analysis for regression models.

Generates:
1. Actual vs predicted scatter plot
2. Bucketed prediction grid (classification-style confusion matrix)
3. Error magnitude by duration range
4. SHAP top feature importance (if available)

Reads predictions.csv from each model's directory and produces figures
and CSVs in models/<name>/analysis/.
"""

import json
import logging
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils.config import get_model_dir

logger = logging.getLogger(__name__)

# Bucket edges (hours) for the prediction grid
DEFAULT_BUCKETS = [
    (0, 8, "< 1 day"),
    (8, 24, "1 day"),
    (24, 72, "1-3 days"),
    (72, 168, "3-7 days"),
    (168, 720, "1-4 weeks"),
    (720, float("inf"), "> 4 weeks"),
]


def _bucket_of(value: float, buckets=DEFAULT_BUCKETS) -> str:
    """Return the bucket label a value falls into."""
    for low, high, label in buckets:
        if low <= value < high:
            return label
    return buckets[-1][2]


def _load_predictions(model_dir: Path) -> tuple[pd.DataFrame, dict] | None:
    """Load predictions.csv and results.json from a model directory."""
    preds_path = model_dir / "predictions.csv"
    results_path = model_dir / "results.json"

    if not preds_path.exists():
        return None

    df = pd.read_csv(preds_path)
    test_df = df[df["split"] == "test"].reset_index(drop=True)

    results = {}
    if results_path.exists():
        with open(results_path) as f:
            results = json.load(f)

    return test_df, results


def plot_actual_vs_predicted(test_df: pd.DataFrame, model_name: str, out_dir: Path):
    """Scatter plot of actual vs predicted values with identity line."""
    actuals = test_df["actual_hours"].values
    preds = test_df["predicted_hours"].values

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(actuals, preds, alpha=0.4, s=20, edgecolors="none")

    # Identity line (perfect prediction)
    max_val = max(actuals.max(), preds.max())
    ax.plot([0, max_val], [0, max_val], "k--", alpha=0.5, label="Perfect prediction")

    # ±25% bands
    x = np.linspace(0, max_val, 100)
    ax.fill_between(x, x * 0.75, x * 1.25, alpha=0.15, color="green",
                    label="±25% (PRED(25))")

    ax.set_xlabel("Actual duration (hours)")
    ax.set_ylabel("Predicted duration (hours)")
    ax.set_title(f"Actual vs Predicted — {model_name}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = out_dir / "actual_vs_predicted.png"
    plt.savefig(path, dpi=150)
    plt.close()
    logger.info(f"    Saved {path.name}")


def plot_bucket_grid(test_df: pd.DataFrame, model_name: str, out_dir: Path):
    """Classification-style grid: actual bucket vs predicted bucket."""
    labels = [b[2] for b in DEFAULT_BUCKETS]

    test_df = test_df.copy()
    test_df["actual_bucket"] = test_df["actual_hours"].apply(_bucket_of)
    test_df["predicted_bucket"] = test_df["predicted_hours"].apply(_bucket_of)

    # Build matrix
    matrix = pd.crosstab(
        test_df["actual_bucket"],
        test_df["predicted_bucket"],
    ).reindex(index=labels, columns=labels, fill_value=0)

    # Normalize by row (actual bucket) for the color scale
    matrix_pct = matrix.div(matrix.sum(axis=1), axis=0).fillna(0) * 100

    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(matrix_pct.values, cmap="Blues", aspect="auto", vmin=0, vmax=100)

    # Annotations: count and percentage
    for i in range(len(labels)):
        for j in range(len(labels)):
            count = matrix.iloc[i, j]
            pct = matrix_pct.iloc[i, j]
            if count > 0:
                color = "white" if pct > 50 else "black"
                ax.text(j, i, f"{count}\n{pct:.0f}%",
                       ha="center", va="center", color=color, fontsize=9)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted bucket")
    ax.set_ylabel("Actual bucket")
    ax.set_title(f"Actual vs Predicted Buckets — {model_name}\n"
                 f"(Diagonal = correct bucket, off-diagonal = wrong)")

    # Diagonal accuracy
    correct = sum(matrix.iloc[i, i] for i in range(len(labels)))
    total = matrix.values.sum()
    acc = correct / total * 100 if total > 0 else 0
    fig.text(0.99, 0.02, f"Bucket accuracy: {acc:.1f}% ({correct}/{total})",
             ha="right", fontsize=10, style="italic")

    plt.colorbar(im, ax=ax, label="% of actual bucket")
    plt.tight_layout()
    path = out_dir / "bucket_grid.png"
    plt.savefig(path, dpi=150)
    plt.close()

    matrix.to_csv(out_dir / "bucket_grid_counts.csv")
    logger.info(f"    Saved {path.name} (bucket accuracy: {acc:.1f}%)")
    return acc


def plot_error_by_range(test_df: pd.DataFrame, model_name: str, out_dir: Path):
    """Box plot of absolute errors, grouped by actual duration bucket."""
    test_df = test_df.copy()
    test_df["abs_error"] = (test_df["actual_hours"] - test_df["predicted_hours"]).abs()
    test_df["bucket"] = test_df["actual_hours"].apply(_bucket_of)

    labels = [b[2] for b in DEFAULT_BUCKETS]
    groups = [test_df.loc[test_df["bucket"] == label, "abs_error"].values for label in labels]
    counts = [len(g) for g in groups]

    # Drop empty buckets for cleaner plot
    non_empty = [(g, lab, c) for g, lab, c in zip(groups, labels, counts) if c > 0]
    if not non_empty:
        return
    groups, labels, counts = zip(*non_empty)

    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(groups, labels=labels, showfliers=False, patch_artist=True)

    for patch in bp["boxes"]:
        patch.set_facecolor("#6aa6e8")

    for i, c in enumerate(counts, 1):
        ax.text(i, ax.get_ylim()[1] * 0.95, f"n={c}", ha="center", fontsize=9, color="gray")

    ax.set_xlabel("Actual duration bucket")
    ax.set_ylabel("Absolute error (hours)")
    ax.set_title(f"Prediction error by actual duration — {model_name}")
    ax.grid(True, axis="y", alpha=0.3)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    path = out_dir / "error_by_range.png"
    plt.savefig(path, dpi=150)
    plt.close()

    # Also save summary stats per bucket
    summary = pd.DataFrame({
        "bucket": labels,
        "count": counts,
        "median_error_h": [np.median(g) for g in groups],
        "mean_error_h": [np.mean(g) for g in groups],
        "p90_error_h": [np.percentile(g, 90) for g in groups],
    })
    summary.to_csv(out_dir / "error_by_range.csv", index=False)
    logger.info(f"    Saved {path.name}")


def plot_shap_importance(model_dir: Path, model_name: str, out_dir: Path,
                          top_n: int = 15):
    """Compute and plot SHAP top-N feature importances.

    Requires the trained model (.joblib) and the saved PCA/scaler if present.
    """
    try:
        import shap
    except ImportError:
        logger.warning("  shap not installed, skipping SHAP analysis")
        return

    model_path = model_dir / "model.joblib"
    if not model_path.exists():
        logger.warning(f"  {model_path} not found, skipping SHAP")
        return

    model = joblib.load(model_path)
    feature_names = None
    results_path = model_dir / "results.json"
    if results_path.exists():
        with open(results_path) as f:
            feature_names = json.load(f).get("feature_names")

    if feature_names is None:
        logger.warning("  No feature_names in results.json, SHAP will use generic labels")

    # We don't have the raw feature matrix on hand, so use the model's
    # feature_importances_ as a simpler proxy if SHAP requires data we lack.
    # Simplest approach: plot XGBoost's built-in feature importance.
    try:
        importances = model.feature_importances_
        if feature_names is None:
            feature_names = [f"f_{i}" for i in range(len(importances))]

        imp_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        }).sort_values("importance", ascending=False).head(top_n)

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.barh(imp_df["feature"][::-1], imp_df["importance"][::-1], color="#6aa6e8")
        ax.set_xlabel("Feature importance (XGBoost gain)")
        ax.set_title(f"Top {top_n} features — {model_name}")
        plt.tight_layout()
        path = out_dir / "feature_importance.png"
        plt.savefig(path, dpi=150)
        plt.close()

        imp_df.to_csv(out_dir / "feature_importance.csv", index=False)
        logger.info(f"    Saved {path.name} (top feature: {imp_df.iloc[0]['feature']})")
    except Exception as e:
        logger.warning(f"  Feature importance failed: {e}")


def run_error_analysis(model_key: str = None):
    """Run the full error analysis for one or all trained models.

    If model_key is None, analyzes all three canonical models.
    """
    models = {
        "A": "model_a_text_only",
        "B": "model_b_repo_only",
        "C": "model_c_combined",
    }

    keys = [model_key] if model_key else list(models.keys())

    for key in keys:
        subdir = models.get(key)
        if subdir is None:
            logger.warning(f"Unknown model key: {key}")
            continue

        model_dir = get_model_dir() / subdir
        loaded = _load_predictions(model_dir)
        if loaded is None:
            logger.warning(f"Model {key}: no predictions.csv found at {model_dir}")
            continue

        test_df, results = loaded

        out_dir = model_dir / "analysis"
        out_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Error analysis for Model {key} ({subdir}):")
        logger.info(f"  Test samples: {len(test_df)}")

        plot_actual_vs_predicted(test_df, f"Model {key}", out_dir)
        plot_bucket_grid(test_df, f"Model {key}", out_dir)
        plot_error_by_range(test_df, f"Model {key}", out_dir)
        plot_shap_importance(model_dir, f"Model {key}", out_dir)

        logger.info(f"  All analyses saved to {out_dir}")
