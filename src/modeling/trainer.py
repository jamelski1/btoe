"""Model training, evaluation, and comparison.

Implements the three model configurations:
- Model A: Text-only (CodeBERT embeddings + derived NLP features)
- Model B: Repo-only (repository-mined features)
- Model C: Combined (NLP + repo features)

All use XGBoost with 5-fold CV and Bayesian hyperparameter optimization.
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import KFold, cross_val_predict
from skopt import BayesSearchCV
from skopt.space import Integer, Real
from xgboost import XGBRegressor

from src.utils.config import load_config

logger = logging.getLogger(__name__)


@dataclass
class ModelResult:
    """Results from training and evaluating a model configuration."""

    name: str
    predictions: np.ndarray
    actuals: np.ndarray
    best_params: dict
    cv_scores: dict
    feature_names: list[str]


class ModelTrainer:
    """Trains and evaluates the three model configurations."""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.model_cfg = self.config["modeling"]
        self.seed = self.model_cfg["random_seed"]

    def get_search_space(self) -> dict:
        """Define Bayesian optimization search space for XGBoost."""
        return {
            "n_estimators": Integer(100, 1000),
            "max_depth": Integer(3, 10),
            "learning_rate": Real(0.01, 0.3, prior="log-uniform"),
            "subsample": Real(0.6, 1.0),
            "colsample_bytree": Real(0.5, 1.0),
            "reg_alpha": Real(1e-3, 10.0, prior="log-uniform"),
            "reg_lambda": Real(1e-3, 10.0, prior="log-uniform"),
            "min_child_weight": Integer(1, 10),
        }

    def train_and_evaluate(
        self, X: pd.DataFrame, y: pd.Series, model_name: str
    ) -> ModelResult:
        """Train a model with Bayesian optimization and cross-validation.

        Args:
            X: Feature matrix
            y: Target variable (duration_hours)
            model_name: Identifier ("model_a", "model_b", "model_c")

        Returns:
            ModelResult with predictions, metrics, and best parameters
        """
        logger.info(f"Training {model_name} with {X.shape[1]} features, {len(y)} samples")

        # Set up base estimator
        base_xgb = XGBRegressor(
            objective="reg:squarederror",
            random_state=self.seed,
            n_jobs=-1,
        )

        # Bayesian hyperparameter search
        bayes_cfg = self.model_cfg["bayes_opt"]
        cv = KFold(
            n_splits=self.model_cfg["cv_folds"],
            shuffle=True,
            random_state=self.seed,
        )

        search = BayesSearchCV(
            estimator=base_xgb,
            search_spaces=self.get_search_space(),
            n_iter=bayes_cfg["n_calls"],
            cv=cv,
            scoring="neg_mean_absolute_error",
            random_state=self.seed,
            n_jobs=-1,
            verbose=0,
        )

        search.fit(X, y)
        logger.info(f"Best params for {model_name}: {search.best_params_}")

        # Get cross-validated predictions using best estimator
        best_model = search.best_estimator_
        cv_predictions = cross_val_predict(best_model, X, y, cv=cv)

        # Compute metrics
        metrics = self.compute_metrics(y.values, cv_predictions)
        logger.info(f"{model_name} metrics: {metrics}")

        return ModelResult(
            name=model_name,
            predictions=cv_predictions,
            actuals=y.values,
            best_params=dict(search.best_params_),
            cv_scores=metrics,
            feature_names=list(X.columns),
        )

    def compute_metrics(self, actuals: np.ndarray, predictions: np.ndarray) -> dict:
        """Compute all evaluation metrics."""
        errors = np.abs(actuals - predictions)
        relative_errors = errors / np.maximum(actuals, 1e-6)

        # Mean baseline for SA
        mean_baseline_errors = np.abs(actuals - np.mean(actuals))

        metrics = {
            "mae": float(np.mean(errors)),
            "mdae": float(np.median(errors)),
            "mre": float(np.mean(relative_errors)),
            "pred_25": float(np.mean(relative_errors <= 0.25) * 100),
            "pred_50": float(np.mean(relative_errors <= 0.50) * 100),
            "r2": float(1 - np.sum(errors**2) / np.sum((actuals - np.mean(actuals))**2)),
            "sa": float(
                (1 - np.sum(errors) / np.sum(mean_baseline_errors)) * 100
                if np.sum(mean_baseline_errors) > 0
                else 0
            ),
        }
        return metrics

    def compare_models(
        self, result_a: ModelResult, result_b: ModelResult, result_c: ModelResult
    ) -> dict:
        """Run statistical comparison between model configurations.

        Performs Wilcoxon signed-rank tests and computes Cliff's delta
        for pairwise model comparisons.
        """
        comparisons = {}
        pairs = [
            ("A_vs_B", result_a, result_b),
            ("A_vs_C", result_a, result_c),
            ("B_vs_C", result_b, result_c),
        ]

        for label, r1, r2 in pairs:
            errors_1 = np.abs(r1.actuals - r1.predictions)
            errors_2 = np.abs(r2.actuals - r2.predictions)

            # Wilcoxon signed-rank test
            stat, p_value = stats.wilcoxon(errors_1, errors_2)

            # Cliff's delta
            delta = self._cliffs_delta(errors_1, errors_2)

            comparisons[label] = {
                "wilcoxon_stat": float(stat),
                "p_value": float(p_value),
                "significant": p_value < self.config["statistics"]["wilcoxon_alpha"],
                "cliffs_delta": delta["delta"],
                "effect_size": delta["interpretation"],
            }

        return comparisons

    def _cliffs_delta(self, x: np.ndarray, y: np.ndarray) -> dict:
        """Compute Cliff's delta effect size."""
        n_x, n_y = len(x), len(y)
        more = sum(1 for xi in x for yi in y if xi > yi)
        less = sum(1 for xi in x for yi in y if xi < yi)
        delta = (more - less) / (n_x * n_y)

        thresholds = self.config["statistics"]["cliff_delta_thresholds"]
        abs_delta = abs(delta)
        if abs_delta < thresholds["negligible"]:
            interpretation = "negligible"
        elif abs_delta < thresholds["small"]:
            interpretation = "small"
        elif abs_delta < thresholds["medium"]:
            interpretation = "medium"
        else:
            interpretation = "large"

        return {"delta": float(delta), "interpretation": interpretation}
