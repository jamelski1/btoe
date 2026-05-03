"""SHAP analysis for trained XGBoost models.

Computes SHAP values using TreeExplainer and generates:
1. Summary plot (beeswarm) — global feature importance with direction
2. Bar plot — mean |SHAP| per feature
3. Per-sample waterfall for selected examples
4. SHAP values CSV for further analysis

References:
  Lundberg, S.M. & Lee, S. (2017). A unified approach to interpreting
  model predictions. NeurIPS 2017, 4765-4774.

Usage:
    python -m src.pipeline --step shap_analysis
"""

import json
import logging
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils.config import get_data_dir, get_model_dir

logger = logging.getLogger(__name__)

MODEL_DIRS = {
    "A": "model_a_text_only",
    "B": "model_b_repo_only",
    "C": "model_c_combined",
}


def _load_test_features(model_key: str):
    """Reconstruct the test-set feature matrix for a trained model.

    Loads the raw data, applies the same filtering and dimensionality
    reduction that training used, and returns the test-set features
    aligned with predictions.csv.
    """
    model_dir = get_model_dir() / MODEL_DIRS[model_key]
    results_path = model_dir / "results.json"

    if not results_path.exists():
        return None, None, None

    with open(results_path) as f:
        results = json.load(f)

    test_indices = results.get("test_indices")
    feature_names = results.get("feature_names")

    if not test_indices or not feature_names:
        return None, None, None

    # Load raw data
    data_dir = get_data_dir()
    parquet_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    csv_path = data_dir / "raw" / "issue_pr_pairs.csv"

    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        return None, None, None

    # Apply duration filter
    mask = (df["duration_hours"] >= 1) & (df["duration_hours"] <= 2160)
    df = df[mask].reset_index(drop=True)

    # Load features
    if model_key == "A":
        feat_path = data_dir / "processed" / "nlp_features.parquet"
    elif model_key == "B":
        feat_path = data_dir / "processed" / "repo_features.parquet"
    else:  # C
        nlp_path = data_dir / "processed" / "nlp_features.parquet"
        repo_path = data_dir / "processed" / "repo_features.parquet"
        if nlp_path.exists() and repo_path.exists():
            nlp = pd.read_parquet(nlp_path)
            repo = pd.read_parquet(repo_path)
            nlp = nlp[mask].reset_index(drop=True)
            repo = repo[mask].reset_index(drop=True)
            features = pd.concat([nlp, repo], axis=1)
        else:
            return None, None, None
        # Get test subset
        test_features = features.iloc[test_indices].reset_index(drop=True)
        # Apply saved transforms
        scaler_path = model_dir / "scaler.joblib"
        reducer_path = model_dir / "reducer.joblib"
        pca_path = model_dir / "pca.joblib"

        transform_obj = None
        if reducer_path.exists():
            transform_obj = joblib.load(reducer_path)
        elif pca_path.exists():
            transform_obj = joblib.load(pca_path)

        if scaler_path.exists() and transform_obj is not None:
            scaler = joblib.load(scaler_path)
            emb_cols = [c for c in test_features.columns if c.startswith("emb_")]
            other_cols = [c for c in test_features.columns if not c.startswith("emb_")]

            if emb_cols:
                emb_scaled = scaler.transform(test_features[emb_cols])
                emb_reduced = transform_obj.transform(emb_scaled)
                n_comp = emb_reduced.shape[1]
                prefix = "pca" if hasattr(transform_obj, "explained_variance_ratio_") else "pls"
                reduced_cols = [f"{prefix}_{i}" for i in range(n_comp)]
                reduced_df = pd.DataFrame(emb_reduced, columns=reduced_cols)
                other_df = test_features[other_cols].reset_index(drop=True)
                test_features = pd.concat([reduced_df, other_df], axis=1)

        # Align to expected feature names
        for col in feature_names:
            if col not in test_features.columns:
                test_features[col] = 0.0
        test_features = test_features[feature_names]

        test_actuals = df.iloc[test_indices]["duration_hours"].values
        return test_features, test_actuals, results

    # For models A and B (simpler path)
    if not feat_path.exists():
        return None, None, None

    features = pd.read_parquet(feat_path)
    features = features[mask].reset_index(drop=True)
    test_features = features.iloc[test_indices].reset_index(drop=True)

    # Apply saved PCA/scaler for Model A
    scaler_path = model_dir / "scaler.joblib"
    reducer_path = model_dir / "reducer.joblib"
    pca_path = model_dir / "pca.joblib"

    transform_obj = None
    if reducer_path.exists():
        transform_obj = joblib.load(reducer_path)
    elif pca_path.exists():
        transform_obj = joblib.load(pca_path)

    if scaler_path.exists() and transform_obj is not None:
        scaler = joblib.load(scaler_path)
        emb_cols = [c for c in test_features.columns if c.startswith("emb_")]
        other_cols = [c for c in test_features.columns if not c.startswith("emb_")]

        if emb_cols:
            emb_scaled = scaler.transform(test_features[emb_cols])
            emb_reduced = transform_obj.transform(emb_scaled)
            n_comp = emb_reduced.shape[1]
            prefix = "pca" if hasattr(transform_obj, "explained_variance_ratio_") else "pls"
            reduced_cols = [f"{prefix}_{i}" for i in range(n_comp)]
            reduced_df = pd.DataFrame(emb_reduced, columns=reduced_cols)
            other_df = test_features[other_cols].reset_index(drop=True)
            test_features = pd.concat([reduced_df, other_df], axis=1)

    # Align to expected feature names
    for col in feature_names:
        if col not in test_features.columns:
            test_features[col] = 0.0
    test_features = test_features[feature_names]

    test_actuals = df.iloc[test_indices]["duration_hours"].values
    return test_features, test_actuals, results


def run_shap_analysis(model_key: str = None, top_n: int = 20):
    """Run SHAP analysis for one or all trained models."""
    try:
        import shap
    except ImportError:
        logger.error("shap not installed. Run: pip install shap")
        return

    keys = [model_key] if model_key else ["A", "B", "C"]

    for key in keys:
        subdir = MODEL_DIRS.get(key)
        if not subdir:
            continue

        model_dir = get_model_dir() / subdir
        model_path = model_dir / "model.joblib"

        if not model_path.exists():
            logger.warning(f"Model {key}: model.joblib not found, skipping")
            continue

        logger.info(f"SHAP analysis for Model {key} ({subdir})")

        # Load model
        model = joblib.load(model_path)

        # Reconstruct test features
        test_features, test_actuals, results = _load_test_features(key)
        if test_features is None:
            logger.warning(f"  Could not reconstruct test features, skipping")
            continue

        logger.info(f"  Test features: {test_features.shape}")

        # Compute SHAP values
        logger.info(f"  Computing SHAP values (TreeExplainer)...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(test_features)

        out_dir = model_dir / "analysis"
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Summary plot (beeswarm)
        logger.info(f"  Generating summary plot...")
        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, test_features, max_display=top_n, show=False)
        plt.title(f"SHAP Feature Importance — Model {key}")
        plt.tight_layout()
        plt.savefig(out_dir / "shap_summary.png", dpi=150, bbox_inches="tight")
        plt.close()

        # 2. Bar plot (mean |SHAP|)
        logger.info(f"  Generating bar plot...")
        plt.figure(figsize=(10, 6))
        shap.plots.bar(shap_values, max_display=top_n, show=False)
        plt.title(f"Mean |SHAP| — Model {key}")
        plt.tight_layout()
        plt.savefig(out_dir / "shap_bar.png", dpi=150, bbox_inches="tight")
        plt.close()

        # 3. Save SHAP values as CSV (mean absolute per feature)
        mean_shap = pd.DataFrame({
            "feature": test_features.columns,
            "mean_abs_shap": np.abs(shap_values.values).mean(axis=0),
        }).sort_values("mean_abs_shap", ascending=False)
        mean_shap.to_csv(out_dir / "shap_values.csv", index=False)

        logger.info(f"  Top 5 SHAP features:")
        for _, row in mean_shap.head(5).iterrows():
            logger.info(f"    {row['feature']}: {row['mean_abs_shap']:.4f}")

        logger.info(f"  Saved to {out_dir}")
