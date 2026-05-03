"""Model training, evaluation, and comparison.

Implements the three model configurations:
- Model A: Text-only (CodeBERT embeddings + derived NLP features)
- Model B: Repo-only (repository-mined features)
- Model C: Combined (NLP + repo features)

All use XGBoost with 5-fold CV and Bayesian hyperparameter optimization.
Uses 80/20 train/test holdout, with 5-fold CV on the training set only.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from sklearn.preprocessing import StandardScaler
from skopt import BayesSearchCV
from skopt.space import Integer, Real
from xgboost import XGBRegressor

from src.utils.config import get_model_dir, load_config

logger = logging.getLogger(__name__)


@dataclass
class ModelResult:
    """Results from training and evaluating a model configuration."""

    name: str
    # Train set (CV predictions)
    train_predictions: np.ndarray
    train_actuals: np.ndarray
    train_metrics: dict
    # Holdout test set
    test_predictions: np.ndarray
    test_actuals: np.ndarray
    test_metrics: dict
    # Model info
    best_params: dict
    feature_names: list[str]
    train_indices: np.ndarray = field(default=None, repr=False)
    test_indices: np.ndarray = field(default=None, repr=False)


class ModelTrainer:
    """Trains and evaluates the three model configurations."""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.model_cfg = self.config["modeling"]
        self.seed = self.model_cfg["random_seed"]

    def reduce_embeddings(self, X: pd.DataFrame, n_components: int = None) -> tuple:
        """Apply PCA to embedding columns, keeping derived features intact.

        Fits PCA on the training data only. Returns reduced features and
        the fitted scaler + PCA objects for transforming test data.

        Embedding columns are identified by the 'emb_' prefix.
        """
        emb_cols = [c for c in X.columns if c.startswith("emb_")]
        other_cols = [c for c in X.columns if not c.startswith("emb_")]

        if not emb_cols:
            logger.info("  No embedding columns found, skipping PCA")
            return X, None, None

        n_emb = len(emb_cols)
        if n_components is None:
            cfg_components = self.config.get("pca", {}).get("n_components", 50)
            n_components = min(cfg_components, len(X) // 5)
        n_components = min(n_components, n_emb, len(X))

        logger.info(f"  PCA: reducing {n_emb} embedding dims -> {n_components} components")

        # Standardize embeddings before PCA
        scaler = StandardScaler()
        emb_scaled = scaler.fit_transform(X[emb_cols])

        pca = PCA(n_components=n_components, random_state=self.seed)
        emb_reduced = pca.fit_transform(emb_scaled)

        variance_explained = pca.explained_variance_ratio_.sum() * 100
        logger.info(f"  PCA: {variance_explained:.1f}% variance retained with {n_components} components")

        # Build new feature DataFrame
        pca_cols = [f"pca_{i}" for i in range(n_components)]
        pca_df = pd.DataFrame(emb_reduced, index=X.index, columns=pca_cols)
        other_df = X[other_cols].reset_index(drop=True)
        pca_df = pca_df.reset_index(drop=True)

        X_reduced = pd.concat([pca_df, other_df], axis=1)
        logger.info(f"  Final feature set: {len(pca_cols)} PCA + {len(other_cols)} derived = {X_reduced.shape[1]} features")

        return X_reduced, scaler, pca

    def transform_embeddings(self, X: pd.DataFrame, scaler, pca) -> pd.DataFrame:
        """Apply a previously fitted PCA transform to new data (e.g., test set)."""
        emb_cols = [c for c in X.columns if c.startswith("emb_")]
        other_cols = [c for c in X.columns if not c.startswith("emb_")]

        if scaler is None or pca is None:
            return X

        emb_scaled = scaler.transform(X[emb_cols])
        emb_reduced = pca.transform(emb_scaled)

        pca_cols = [f"pca_{i}" for i in range(emb_reduced.shape[1])]
        pca_df = pd.DataFrame(emb_reduced, index=X.index, columns=pca_cols)
        other_df = X[other_cols].reset_index(drop=True)
        pca_df = pca_df.reset_index(drop=True)

        return pd.concat([pca_df, other_df], axis=1)

    def select_topk_embeddings(self, X: pd.DataFrame, y: pd.Series,
                                 k: int = None) -> tuple:
        """Select top-K embedding dimensions by F-statistic with target.

        Like reduce_embeddings but uses supervised feature selection (Top-K
        by f_regression) instead of unsupervised PCA. The 6 derived NLP
        features and any non-embedding columns are always retained.

        Returns (X_selected, scaler, selector).
        """
        emb_cols = [c for c in X.columns if c.startswith("emb_")]
        other_cols = [c for c in X.columns if not c.startswith("emb_")]

        if not emb_cols:
            logger.info("  No embedding columns found, skipping Top-K")
            return X, None, None

        n_emb = len(emb_cols)
        if k is None:
            cfg_k = self.config.get("topk", {}).get("k", 50)
            k = min(cfg_k, len(X) // 5)
        k = min(k, n_emb)

        logger.info(f"  Top-K: selecting {k}/{n_emb} embedding dims by F-statistic")

        # Standardize before selection (consistent with PCA path)
        scaler = StandardScaler()
        emb_scaled = scaler.fit_transform(X[emb_cols])

        selector = SelectKBest(score_func=f_regression, k=k)
        emb_selected = selector.fit_transform(emb_scaled, y)

        selected_idx = selector.get_support(indices=True)
        # Show top scores (informative)
        top_scores = sorted(selector.scores_[selected_idx], reverse=True)[:5]
        logger.info(f"  Top-K: top-5 F-scores: {[f'{s:.1f}' for s in top_scores]}")

        topk_cols = [f"topk_{emb_cols[i].replace('emb_', '')}" for i in selected_idx]
        topk_df = pd.DataFrame(emb_selected, index=X.index, columns=topk_cols)
        other_df = X[other_cols].reset_index(drop=True)
        topk_df = topk_df.reset_index(drop=True)

        X_selected = pd.concat([topk_df, other_df], axis=1)
        logger.info(f"  Final feature set: {len(topk_cols)} Top-K + {len(other_cols)} derived = {X_selected.shape[1]} features")

        return X_selected, scaler, selector

    def transform_topk_embeddings(self, X: pd.DataFrame, scaler, selector) -> pd.DataFrame:
        """Apply a previously fitted Top-K selection to new data."""
        emb_cols = [c for c in X.columns if c.startswith("emb_")]
        other_cols = [c for c in X.columns if not c.startswith("emb_")]

        if scaler is None or selector is None:
            return X

        emb_scaled = scaler.transform(X[emb_cols])
        emb_selected = selector.transform(emb_scaled)

        selected_idx = selector.get_support(indices=True)
        topk_cols = [f"topk_{emb_cols[i].replace('emb_', '')}" for i in selected_idx]
        topk_df = pd.DataFrame(emb_selected, index=X.index, columns=topk_cols)
        other_df = X[other_cols].reset_index(drop=True)
        topk_df = topk_df.reset_index(drop=True)

        return pd.concat([topk_df, other_df], axis=1)

    def reduce_embeddings_pls(self, X: pd.DataFrame, y: pd.Series,
                               n_components: int = None) -> tuple:
        """Apply PLS to embedding columns, keeping derived features intact.

        PLS (Partial Least Squares) finds linear combinations of X that
        maximize covariance with y — supervised dimensionality reduction.
        """
        emb_cols = [c for c in X.columns if c.startswith("emb_")]
        other_cols = [c for c in X.columns if not c.startswith("emb_")]

        if not emb_cols:
            logger.info("  No embedding columns found, skipping PLS")
            return X, None, None

        n_emb = len(emb_cols)
        if n_components is None:
            cfg_k = self.config.get("pls", {}).get("n_components", 50)
            n_components = min(cfg_k, len(X) // 5)
        n_components = min(n_components, n_emb, len(X))

        logger.info(f"  PLS: reducing {n_emb} embedding dims -> {n_components} components")

        scaler = StandardScaler()
        emb_scaled = scaler.fit_transform(X[emb_cols])

        pls = PLSRegression(n_components=n_components)
        emb_pls = pls.fit_transform(emb_scaled, y)[0]

        logger.info(f"  PLS: {n_components} components fitted (supervised on target)")

        pls_cols = [f"pls_{i}" for i in range(n_components)]
        pls_df = pd.DataFrame(emb_pls, index=X.index, columns=pls_cols)
        other_df = X[other_cols].reset_index(drop=True)
        pls_df = pls_df.reset_index(drop=True)

        X_reduced = pd.concat([pls_df, other_df], axis=1)
        logger.info(f"  Final feature set: {len(pls_cols)} PLS + {len(other_cols)} derived = {X_reduced.shape[1]} features")

        return X_reduced, scaler, pls

    def transform_embeddings_pls(self, X: pd.DataFrame, scaler, pls) -> pd.DataFrame:
        """Apply a previously fitted PLS transform to new data."""
        emb_cols = [c for c in X.columns if c.startswith("emb_")]
        other_cols = [c for c in X.columns if not c.startswith("emb_")]

        if scaler is None or pls is None:
            return X

        emb_scaled = scaler.transform(X[emb_cols])
        emb_pls = pls.transform(emb_scaled)

        pls_cols = [f"pls_{i}" for i in range(emb_pls.shape[1])]
        pls_df = pd.DataFrame(emb_pls, index=X.index, columns=pls_cols)
        other_df = X[other_cols].reset_index(drop=True)
        pls_df = pls_df.reset_index(drop=True)

        return pd.concat([pls_df, other_df], axis=1)

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
        """Train a model with 80/20 holdout, Bayesian optimization, and 5-fold CV.

        1. Split data into 80% train / 20% test holdout
        2. Run Bayesian optimization with 5-fold CV on training set
        3. Evaluate best model on held-out test set
        4. Save model and results to disk

        Args:
            X: Feature matrix
            y: Target variable (duration_hours)
            model_name: Identifier ("model_a", "model_b", "model_c")

        Returns:
            ModelResult with train/test predictions, metrics, and best parameters
        """
        total_start = time.time()
        test_size = self.model_cfg["test_size"]

        logger.info(f"{'='*60}")
        logger.info(f"Training {model_name}")
        logger.info(f"  Features: {X.shape[1]}, Samples: {len(y)}")
        logger.info(f"  Split: {(1-test_size)*100:.0f}% train / {test_size*100:.0f}% test")
        logger.info(f"{'='*60}")

        # --- Step 1: 80/20 holdout split ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.seed
        )
        logger.info(f"  Train set: {len(X_train)} samples")
        logger.info(f"  Test set:  {len(X_test)} samples")
        logger.info(f"  Target stats (train): mean={y_train.mean():.1f}h, median={y_train.median():.1f}h, std={y_train.std():.1f}h")
        logger.info(f"  Target stats (test):  mean={y_test.mean():.1f}h, median={y_test.median():.1f}h, std={y_test.std():.1f}h")

        # --- Log-transform target to handle skewed distribution ---
        y_train_log = np.log1p(y_train)
        y_test_log = np.log1p(y_test)
        logger.info(f"  Log-transformed target: train range [{y_train_log.min():.2f}, {y_train_log.max():.2f}], "
                     f"test range [{y_test_log.min():.2f}, {y_test_log.max():.2f}]")

        # --- Feature selection on embeddings (fit on train only) ---
        # Selection method: "pca" (default), "topk", "pls", or "none"
        method = self.config.get("feature_selection", {}).get("method", "pca")
        emb_cols = [c for c in X_train.columns if c.startswith("emb_")]

        # reducer stores the fitted transform object (PCA, PLS, or SelectKBest)
        scaler, reducer = None, None

        if not emb_cols:
            pass
        elif method == "none":
            logger.info(f"  No dimensionality reduction: using all {len(emb_cols)} embedding dims + "
                        f"{len(X_train.columns) - len(emb_cols)} derived = {len(X_train.columns)} features")
        elif method == "topk":
            X_train, scaler, reducer = self.select_topk_embeddings(X_train, y_train)
            X_test = self.transform_topk_embeddings(X_test, scaler, reducer)
        elif method == "pls":
            X_train, scaler, reducer = self.reduce_embeddings_pls(X_train, y_train_log)
            X_test = self.transform_embeddings_pls(X_test, scaler, reducer)
        else:  # pca (default)
            X_train, scaler, reducer = self.reduce_embeddings(X_train)
            X_test = self.transform_embeddings(X_test, scaler, reducer)

        # --- Step 2: Bayesian hyperparameter optimization on train set ---
        logger.info(f"  Starting Bayesian optimization ({self.model_cfg['bayes_opt']['n_calls']} iterations, {self.model_cfg['cv_folds']}-fold CV)...")
        bayes_start = time.time()

        base_xgb = XGBRegressor(
            objective="reg:squarederror",
            random_state=self.seed,
            n_jobs=-1,
        )

        cv = KFold(
            n_splits=self.model_cfg["cv_folds"],
            shuffle=True,
            random_state=self.seed,
        )

        bayes_cfg = self.model_cfg["bayes_opt"]
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

        # Fit with progress callback
        iteration_count = [0]
        def on_step(result):
            iteration_count[0] += 1
            i = iteration_count[0]
            best = -result.fun
            if i == 1 or i % 10 == 0 or i == bayes_cfg["n_calls"]:
                elapsed = time.time() - bayes_start
                logger.info(f"    Iteration {i}/{bayes_cfg['n_calls']}: best log-MAE={best:.4f} ({elapsed:.0f}s elapsed)")
            return False  # don't stop early

        search.fit(X_train, y_train_log, callback=on_step)

        bayes_elapsed = time.time() - bayes_start
        logger.info(f"  Bayesian optimization complete in {bayes_elapsed/60:.1f} min")
        logger.info(f"  Best params: {dict(search.best_params_)}")
        logger.info(f"  Best CV log-MAE: {-search.best_score_:.4f}")

        # --- Step 3: Cross-validated predictions on train set ---
        logger.info(f"  Computing 5-fold CV predictions on training set...")
        best_model = search.best_estimator_
        train_cv_preds_log = cross_val_predict(best_model, X_train, y_train_log, cv=cv)

        # Convert back to original hours for metrics
        train_cv_predictions = np.expm1(train_cv_preds_log)
        train_cv_predictions = np.maximum(train_cv_predictions, 0)  # clip negatives

        train_metrics = self.compute_metrics(y_train.values, train_cv_predictions,
                                                train_actuals=y_train.values)
        logger.info(f"  Train CV metrics (in original hours):")
        self._log_metrics(train_metrics)

        # --- Step 4: Evaluate on held-out test set ---
        logger.info(f"  Evaluating on held-out test set ({len(X_test)} samples)...")
        best_model.fit(X_train, y_train_log)  # refit on full training set
        test_preds_log = best_model.predict(X_test)

        # Convert back to original hours
        test_predictions = np.expm1(test_preds_log)
        test_predictions = np.maximum(test_predictions, 0)

        test_metrics = self.compute_metrics(y_test.values, test_predictions,
                                              train_actuals=y_train.values)
        logger.info(f"  Test set metrics:")
        self._log_metrics(test_metrics)

        # --- Step 5: Save model and results ---
        result = ModelResult(
            name=model_name,
            train_predictions=train_cv_predictions,
            train_actuals=y_train.values,
            train_metrics=train_metrics,
            test_predictions=test_predictions,
            test_actuals=y_test.values,
            test_metrics=test_metrics,
            best_params=dict(search.best_params_),
            feature_names=list(X_train.columns),
            train_indices=X_train.index.values,
            test_indices=X_test.index.values,
        )

        self._save_result(result, best_model, scaler=scaler, reducer=reducer, method=method)

        total_elapsed = time.time() - total_start
        logger.info(f"{'='*60}")
        logger.info(f"{model_name} complete in {total_elapsed/60:.1f} min")
        logger.info(f"{'='*60}")

        return result

    def _log_metrics(self, metrics: dict):
        """Log metrics in a readable format."""
        logger.info(f"    MAE:      {metrics['mae']:.2f}h")
        logger.info(f"    MdAE:     {metrics['mdae']:.2f}h")
        logger.info(f"    MMRE:     {metrics['mre']:.2%}")
        logger.info(f"    PRED(25): {metrics['pred_25']:.1f}%")
        logger.info(f"    PRED(50): {metrics['pred_50']:.1f}%")
        logger.info(f"    R2:       {metrics['r2']:.4f}")
        logger.info(f"    SA:       {metrics['sa']:.1f}%")

    def _save_result(self, result: ModelResult, model: XGBRegressor,
                      scaler=None, reducer=None, method="pca"):
        """Save model artifact and results JSON to disk."""
        model_dir = get_model_dir() / result.name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save scaler and reducer
        if scaler is not None:
            joblib.dump(scaler, model_dir / "scaler.joblib")
        if reducer is not None:
            # Save under a generic name + method-specific name for compatibility
            joblib.dump(reducer, model_dir / "reducer.joblib")
            if method == "pca":
                joblib.dump(reducer, model_dir / "pca.joblib")
                logger.info(f"  PCA ({reducer.n_components_} components, "
                            f"{reducer.explained_variance_ratio_.sum()*100:.1f}% variance) saved")
            elif method == "topk":
                joblib.dump(reducer, model_dir / "selector.joblib")
                logger.info(f"  Top-K selector ({reducer.k} features) saved")
            elif method == "pls":
                logger.info(f"  PLS ({reducer.n_components} components) saved")

        # Save trained model
        model_path = model_dir / "model.joblib"
        joblib.dump(model, model_path)
        logger.info(f"  Model saved to {model_path}")

        # Save results JSON
        results_dict = {
            "name": result.name,
            "train_metrics": result.train_metrics,
            "test_metrics": result.test_metrics,
            "best_params": result.best_params,
            "feature_names": result.feature_names,
            "n_features": len(result.feature_names),
            "n_train": len(result.train_actuals),
            "n_test": len(result.test_actuals),
            "train_indices": result.train_indices.tolist(),
            "test_indices": result.test_indices.tolist(),
        }
        results_path = model_dir / "results.json"
        with open(results_path, "w") as f:
            json.dump(results_dict, f, indent=2)
        logger.info(f"  Results saved to {results_path}")

        # Save predictions for later analysis
        preds_df = pd.DataFrame({
            "split": (["train"] * len(result.train_actuals) +
                      ["test"] * len(result.test_actuals)),
            "actual_hours": np.concatenate([result.train_actuals, result.test_actuals]),
            "predicted_hours": np.concatenate([result.train_predictions, result.test_predictions]),
        })
        preds_path = model_dir / "predictions.csv"
        preds_df.to_csv(preds_path, index=False)
        logger.info(f"  Predictions saved to {preds_path}")

    def compute_metrics(self, actuals: np.ndarray, predictions: np.ndarray,
                         train_actuals: np.ndarray = None) -> dict:
        """Compute all evaluation metrics.

        Args:
            actuals: True values
            predictions: Model predictions
            train_actuals: Training set actuals for proper SA random baseline.
                If None, uses test actuals as the sampling distribution (less rigorous).
        """
        errors = np.abs(actuals - predictions)
        relative_errors = errors / np.maximum(actuals, 1e-6)

        # SA: Standardized Accuracy (Shepperd & MacDonell, 2012)
        # Proper computation: MAE of random guessing is estimated by
        # sampling 1,000 times from the training distribution and averaging.
        sa_baseline_source = train_actuals if train_actuals is not None else actuals
        sa = self._compute_sa(errors, actuals, sa_baseline_source)

        metrics = {
            "mae": float(np.mean(errors)),
            "mdae": float(np.median(errors)),
            "mre": float(np.mean(relative_errors)),
            "pred_25": float(np.mean(relative_errors <= 0.25) * 100),
            "pred_50": float(np.mean(relative_errors <= 0.50) * 100),
            "r2": float(1 - np.sum(errors**2) / np.sum((actuals - np.mean(actuals))**2)),
            "sa": sa,
        }
        return metrics

    def _compute_sa(self, model_errors: np.ndarray, test_actuals: np.ndarray,
                     train_actuals: np.ndarray, n_runs: int = 1000) -> float:
        """Compute Standardized Accuracy with proper random baseline.

        SA = 1 - (MAE_model / MAE_random) × 100

        MAE_random is computed by:
        1. Randomly sampling (with replacement) from train_actuals
        2. Using each sample as a "prediction" for a test sample
        3. Computing MAE of these random predictions
        4. Repeating n_runs times and averaging

        This follows Shepperd & MacDonell (2012) and addresses the
        methodological concern raised by Tawosi et al. (2023) about
        single-run random baselines.

        References:
            Shepperd, M. & MacDonell, S. (2012). Evaluating prediction
            systems in software project estimation. IST, 54(8), 820-827.
        """
        rng = np.random.RandomState(self.seed)
        n_test = len(test_actuals)
        model_mae = float(np.mean(model_errors))

        random_maes = []
        for _ in range(n_runs):
            random_preds = rng.choice(train_actuals, size=n_test, replace=True)
            random_errors = np.abs(test_actuals - random_preds)
            random_maes.append(float(np.mean(random_errors)))

        mean_random_mae = float(np.mean(random_maes))

        if mean_random_mae == 0:
            return 0.0

        return float((1 - model_mae / mean_random_mae) * 100)

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
            errors_1 = np.abs(r1.test_actuals - r1.test_predictions)
            errors_2 = np.abs(r2.test_actuals - r2.test_predictions)

            # Wilcoxon signed-rank test
            stat, p_value = stats.wilcoxon(errors_1, errors_2)

            # Cliff's delta
            delta = self._cliffs_delta(errors_1, errors_2)

            comparisons[label] = {
                "wilcoxon_stat": float(stat),
                "p_value": float(p_value),
                "significant": bool(p_value < self.config["statistics"]["wilcoxon_alpha"]),
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
