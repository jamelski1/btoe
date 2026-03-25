"""SHAP-based feature importance analysis and error analysis."""

import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from xgboost import XGBRegressor

from src.utils.config import get_model_dir

logger = logging.getLogger(__name__)


class SHAPAnalyzer:
    """Performs SHAP feature importance and error analysis."""

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or get_model_dir() / "figures"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def compute_shap_values(
        self, model: XGBRegressor, X: pd.DataFrame
    ) -> shap.Explanation:
        """Compute SHAP values for a trained model."""
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X)
        return shap_values

    def plot_feature_importance(
        self, shap_values: shap.Explanation, model_name: str, top_n: int = 20
    ):
        """Generate and save SHAP summary plot."""
        fig, ax = plt.subplots(figsize=(10, 8))
        shap.summary_plot(shap_values, max_display=top_n, show=False)
        plt.title(f"Feature Importance — {model_name}")
        plt.tight_layout()
        plt.savefig(self.output_dir / f"shap_{model_name}.png", dpi=150)
        plt.close()
        logger.info(f"Saved SHAP plot for {model_name}")

    def error_analysis(
        self,
        actuals: np.ndarray,
        predictions: np.ndarray,
        X: pd.DataFrame,
        model_name: str,
        worst_pct: float = 0.1,
    ) -> pd.DataFrame:
        """Analyze the worst predictions to identify systematic error patterns."""
        errors = np.abs(actuals - predictions)
        relative_errors = errors / np.maximum(actuals, 1e-6)

        # Identify worst predictions
        threshold = np.percentile(relative_errors, (1 - worst_pct) * 100)
        worst_mask = relative_errors >= threshold

        summary = {
            "total_samples": len(actuals),
            "worst_count": int(worst_mask.sum()),
            "worst_mean_error_hours": float(errors[worst_mask].mean()),
            "worst_mean_actual_hours": float(actuals[worst_mask].mean()),
            "overall_mean_actual_hours": float(actuals.mean()),
        }

        # Compare feature distributions: worst vs rest
        worst_features = X[worst_mask].describe().T
        rest_features = X[~worst_mask].describe().T

        comparison = pd.DataFrame({
            "worst_mean": worst_features["mean"],
            "rest_mean": rest_features["mean"],
            "ratio": worst_features["mean"] / rest_features["mean"].replace(0, np.nan),
        }).sort_values("ratio", ascending=False)

        comparison.to_csv(self.output_dir / f"error_analysis_{model_name}.csv")
        logger.info(f"Error analysis for {model_name}: {summary}")

        return comparison
