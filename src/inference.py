"""Inference module — predict issue resolution duration from trained models.

Supports three model variants:
  Model A  text-only      CodeBERT embeddings + NLP-derived features
  Model B  repo-only      Repository structural features (PyDriller)
  Model C  combined       NLP + repo features

When a GitHub repo URL is provided, PyDriller extracts real structural
features (churn, coupling, file age) from the cloned repository.
Without a repo URL, git history features are zero-padded and only
num_files is used for Models B and C.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.feature_extraction.nlp_features import NLPFeatureExtractor
from src.utils.config import get_model_dir, load_config

logger = logging.getLogger(__name__)

# Column definitions that match feature_extraction outputs exactly
NLP_DERIVED_COLS = [
    "complexity_score",
    "cross_ref_density",
    "ambiguity_index",
    "technical_scope",
    "text_length",
    "word_count",
]

REPO_FEATURE_COLS = [
    "num_files",
    "fan_in",
    "fan_out",
    "total_churn_added",
    "total_churn_deleted",
    "total_churn_commits",
    "avg_churn_per_file",
    "change_impact_radius",
    "avg_file_age_days",
    "min_file_age_days",
    "max_file_age_days",
    "avg_change_frequency",
    "max_change_frequency",
]

MODEL_DIRS = {
    "a": "model_a_text_only",
    "b": "model_b_repo_only",
    "c": "model_c_combined",
}


class ModelPredictor:
    """Loads trained XGBoost models and runs inference for new requirements."""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self._bundles: dict = {}   # key -> loaded bundle
        self._nlp: NLPFeatureExtractor | None = None

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _load(self, key: str) -> dict | None:
        """Return model bundle for *key* ('a', 'b', or 'c'), cached.

        Returns None when the model has not been trained yet.
        """
        if key in self._bundles:
            return self._bundles[key]

        model_dir = get_model_dir() / MODEL_DIRS[key]
        model_path = model_dir / "model.joblib"
        if not model_path.exists():
            return None

        bundle: dict = {
            "model": joblib.load(model_path),
            "scaler": (
                joblib.load(model_dir / "scaler.joblib")
                if (model_dir / "scaler.joblib").exists()
                else None
            ),
            "pca": (
                joblib.load(model_dir / "pca.joblib")
                if (model_dir / "pca.joblib").exists()
                else None
            ),
            "results": {},
        }
        results_path = model_dir / "results.json"
        if results_path.exists():
            with open(results_path) as f:
                bundle["results"] = json.load(f)

        self._bundles[key] = bundle
        logger.info("Loaded model_%s from %s", key, model_dir)
        return bundle

    def _nlp_extractor(self) -> NLPFeatureExtractor:
        if self._nlp is None:
            self._nlp = NLPFeatureExtractor(self.config)
        return self._nlp

    def _extract_nlp(
        self,
        issue_title: str,
        issue_body: str,
        pr_title: str = "",
        pr_body: str = "",
    ) -> pd.DataFrame:
        """Return a single-row NLP feature DataFrame (emb_* + derived cols)."""
        df = pd.DataFrame(
            [
                {
                    "issue_title": issue_title,
                    "issue_body": issue_body,
                    "pr_title": pr_title,
                    "pr_body": pr_body,
                }
            ]
        )
        return self._nlp_extractor().extract_all_features(df)

    def _apply_pca(self, features: pd.DataFrame, bundle: dict) -> pd.DataFrame:
        """Apply the bundle's saved scaler + PCA to emb_* columns only."""
        scaler = bundle["scaler"]
        pca = bundle["pca"]
        if scaler is None or pca is None:
            return features

        emb_cols = [c for c in features.columns if c.startswith("emb_")]
        other_cols = [c for c in features.columns if not c.startswith("emb_")]

        emb_scaled = scaler.transform(features[emb_cols])
        emb_pca = pca.transform(emb_scaled)

        pca_df = pd.DataFrame(
            emb_pca,
            columns=[f"pca_{i}" for i in range(emb_pca.shape[1])],
            index=features.index,
        )
        return pd.concat(
            [pca_df, features[other_cols].reset_index(drop=True)], axis=1
        )

    def _predict(
        self, features: pd.DataFrame, key: str
    ) -> tuple[float | None, str | None]:
        """Align features, run the model, and convert log-hours → hours."""
        bundle = self._load(key)
        if bundle is None:
            return None, "Model not trained yet"

        model = bundle["model"]
        expected: list[str] | None = bundle["results"].get("feature_names")

        if expected:
            # Add any columns the model expects that we don't have (zero-fill)
            for col in expected:
                if col not in features.columns:
                    features[col] = 0.0
            # Drop extra columns and enforce order
            available = [c for c in expected if c in features.columns]
            features = features[available]
            if len(available) < len(expected):
                missing = [c for c in expected if c not in features.columns]
                return None, f"Missing {len(missing)} features (e.g. {missing[0]})"

        try:
            pred_log = model.predict(features)
            hours = float(max(np.expm1(pred_log)[0], 0.0))
            return hours, None
        except Exception as exc:
            return None, str(exc)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def predict_text_only(
        self,
        issue_title: str,
        issue_body: str,
        pr_title: str = "",
        pr_body: str = "",
    ) -> tuple[float | None, str | None]:
        """Model A — text-only prediction (CodeBERT + NLP features)."""
        bundle = self._load("a")
        if bundle is None:
            return None, "Model not trained yet"
        features = self._extract_nlp(issue_title, issue_body, pr_title, pr_body)
        features = self._apply_pca(features, bundle)
        return self._predict(features, "a")

    def _extract_repo_features(
        self, repo_url: str, files: list[str]
    ) -> tuple[pd.DataFrame, bool]:
        """Extract real repo features from a cloned repository.

        Returns (features_df, used_real_features). If cloning or PyDriller
        fails, falls back to zero-padded features.
        """
        from src.data_collection.repo_cloner import RepoCloner
        from src.feature_extraction.repo_features import RepoFeatureExtractor

        if not repo_url:
            row = {col: 0.0 for col in REPO_FEATURE_COLS}
            row["num_files"] = float(len(files))
            return pd.DataFrame([row]), False

        # Parse owner/name from URL
        # Handles: https://github.com/owner/name, github.com/owner/name, owner/name
        repo_url = repo_url.strip().rstrip("/")
        if "github.com" in repo_url:
            parts = repo_url.split("github.com/")[-1].split("/")
        else:
            parts = repo_url.split("/")

        if len(parts) < 2:
            logger.warning(f"Could not parse repo URL: {repo_url}")
            row = {col: 0.0 for col in REPO_FEATURE_COLS}
            row["num_files"] = float(len(files))
            return pd.DataFrame([row]), False

        owner, name = parts[0], parts[1].replace(".git", "")

        try:
            logger.info(f"Cloning/updating {owner}/{name} for feature extraction...")
            cloner = RepoCloner()
            repo_path = cloner.clone_or_update(owner, name)

            # Build a minimal DataFrame that RepoFeatureExtractor expects
            dummy_df = pd.DataFrame([{
                "issue_created_at": datetime.now().isoformat(),
                "pr_files_changed": "|".join(files) if files else "",
            }])

            extractor = RepoFeatureExtractor(str(repo_path), self.config)
            features = extractor.extract_all_features(dummy_df)
            logger.info(f"Extracted real repo features from {owner}/{name}")
            return features, True

        except Exception as e:
            logger.warning(f"PyDriller extraction failed for {repo_url}: {e}")
            row = {col: 0.0 for col in REPO_FEATURE_COLS}
            row["num_files"] = float(len(files))
            return pd.DataFrame([row]), False

    def predict_repo_only(
        self, files: list[str], repo_url: str = ""
    ) -> tuple[float | None, str | None]:
        """Model B — repo-only prediction.

        When repo_url is provided, clones the repo and extracts real
        structural features via PyDriller. Otherwise zero-pads history
        features and uses only num_files.
        """
        bundle = self._load("b")
        if bundle is None:
            return None, "Model not trained yet"
        features, used_real = self._extract_repo_features(repo_url, files)
        return self._predict(features, "b")

    def predict_combined(
        self,
        issue_title: str,
        issue_body: str,
        pr_title: str = "",
        pr_body: str = "",
        files: list[str] = None,
        repo_url: str = "",
    ) -> tuple[float | None, str | None]:
        """Model C — combined NLP + repo features."""
        bundle = self._load("c")
        if bundle is None:
            return None, "Model not trained yet"

        files = files or []
        nlp = self._extract_nlp(issue_title, issue_body, pr_title, pr_body)
        nlp = self._apply_pca(nlp, bundle)

        repo_df, used_real = self._extract_repo_features(repo_url, files)

        features = pd.concat(
            [nlp.reset_index(drop=True), repo_df.reset_index(drop=True)], axis=1
        )
        return self._predict(features, "c")

    def get_metrics(self, key: str) -> dict:
        """Return test-set metrics for a model, or {} if not available."""
        bundle = self._load(key)
        if bundle is None:
            return {}
        return bundle["results"].get("test_metrics", {})

    def is_available(self, key: str) -> bool:
        """True if the model has been trained and saved to disk."""
        return self._load(key) is not None
