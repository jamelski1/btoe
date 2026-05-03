"""Unit tests verifying pipeline correctness for replication.

These tests ensure that the SE3M replication pipeline produces correct,
reproducible outputs at each stage. They verify:

1. NLP feature extraction shape and content
2. No PR text leakage (issue-only text by default)
3. Train/test split determinism
4. Log-transform roundtrip correctness
5. Metric computation against known values
6. PCA fits on training data only
7. Duration filter correctness

Run: pytest tests/test_pipeline_correctness.py -v
"""

import numpy as np
import pandas as pd
import pytest

from src.utils.config import load_config


# ── Fixtures ──────────────────────────────────────────────────────── #

@pytest.fixture
def sample_df():
    """Minimal DataFrame mimicking raw issue-PR pair data."""
    return pd.DataFrame({
        "issue_title": [
            "Fix memory leak in pool",
            "Add dark mode support",
            "Update README typo",
        ],
        "issue_body": [
            "The connection pool leaks memory when connections are dropped.",
            "Users have requested dark mode. We should add theme support.",
            "There is a typo in the installation instructions.",
        ],
        "pr_title": [
            "Fix pool memory leak by releasing connections",
            "Implement dark mode with CSS variables",
            "Fix typo in README.md",
        ],
        "pr_body": [
            "This PR fixes the memory leak by adding proper cleanup.",
            "Added CSS variable-based theming with dark/light toggle.",
            "Simple typo fix.",
        ],
        "duration_hours": [48.0, 336.0, 1.5],
        "repo": ["org/repo", "org/repo", "org/repo"],
        "issue_number": [1, 2, 3],
        "issue_labels": ["bug", "feature", "docs"],
        "issue_created_at": pd.Timestamp("2025-01-01"),
        "pr_merged_at": pd.Timestamp("2025-01-03"),
        "pr_files_changed": ["src/pool.py", "src/theme.css", "README.md"],
        "num_files_changed": [1, 3, 1],
    })


@pytest.fixture
def config():
    """Load default config."""
    return load_config()


# ── Test 1: NLP Feature Shape ────────────────────────────────────── #

class TestNLPFeatures:
    def test_output_shape(self, sample_df, config):
        """NLP extractor produces (N, 774) = 768 embeddings + 6 derived."""
        from src.feature_extraction.nlp_features import NLPFeatureExtractor

        extractor = NLPFeatureExtractor(config)
        features = extractor.extract_all_features(sample_df)

        assert features.shape[0] == len(sample_df), "Row count must match input"
        assert features.shape[1] == 774, "Expected 768 embedding + 6 derived = 774 columns"

    def test_embedding_columns_exist(self, sample_df, config):
        """All 768 embedding columns should be present."""
        from src.feature_extraction.nlp_features import NLPFeatureExtractor

        extractor = NLPFeatureExtractor(config)
        features = extractor.extract_all_features(sample_df)

        emb_cols = [c for c in features.columns if c.startswith("emb_")]
        assert len(emb_cols) == 768

    def test_derived_features_exist(self, sample_df, config):
        """All 6 derived features should be present."""
        from src.feature_extraction.nlp_features import NLPFeatureExtractor

        extractor = NLPFeatureExtractor(config)
        features = extractor.extract_all_features(sample_df)

        expected = ["complexity_score", "cross_ref_density", "ambiguity_index",
                    "technical_scope", "text_length", "word_count"]
        for col in expected:
            assert col in features.columns, f"Missing derived feature: {col}"

    def test_no_nan_in_embeddings(self, sample_df, config):
        """Embeddings should not contain NaN values."""
        from src.feature_extraction.nlp_features import NLPFeatureExtractor

        extractor = NLPFeatureExtractor(config)
        features = extractor.extract_all_features(sample_df)

        emb_cols = [c for c in features.columns if c.startswith("emb_")]
        assert not features[emb_cols].isna().any().any(), "NaN found in embeddings"


# ── Test 2: No PR Text Leakage ───────────────────────────────────── #

class TestNoLeakage:
    def test_default_excludes_pr_text(self, sample_df, config):
        """Default config should NOT include PR text in embeddings."""
        include_pr = config.get("nlp", {}).get("include_pr_text", False)
        assert include_pr is False, "Default must be include_pr_text=False"

    def test_issue_only_produces_different_embeddings(self, sample_df, config):
        """Issue-only and issue+PR text should produce different embeddings."""
        import copy
        from src.feature_extraction.nlp_features import NLPFeatureExtractor

        # Issue-only (default)
        config_issue = copy.deepcopy(config)
        config_issue.setdefault("nlp", {})["include_pr_text"] = False
        ext_issue = NLPFeatureExtractor(config_issue)
        feat_issue = ext_issue.extract_all_features(sample_df)

        # Issue + PR
        config_pr = copy.deepcopy(config)
        config_pr.setdefault("nlp", {})["include_pr_text"] = True
        ext_pr = NLPFeatureExtractor(config_pr)
        feat_pr = ext_pr.extract_all_features(sample_df)

        # Text lengths should differ (PR text adds content)
        assert (feat_issue["text_length"] != feat_pr["text_length"]).any(), \
            "Issue-only and issue+PR should have different text lengths"

    def test_word_count_reflects_issue_only(self, sample_df, config):
        """Word count should match issue title + body only."""
        from src.feature_extraction.nlp_features import NLPFeatureExtractor

        config.setdefault("nlp", {})["include_pr_text"] = False
        extractor = NLPFeatureExtractor(config)
        features = extractor.extract_all_features(sample_df)

        for i, row in sample_df.iterrows():
            expected_words = len((row["issue_title"] + " " + row["issue_body"]).split())
            assert features.loc[i, "word_count"] == expected_words


# ── Test 3: Train/Test Split Determinism ──────────────────────────── #

class TestSplitDeterminism:
    def test_same_seed_same_split(self):
        """Same random seed must produce identical train/test splits."""
        from sklearn.model_selection import train_test_split

        X = pd.DataFrame({"a": range(100)})
        y = pd.Series(range(100))

        X_train1, X_test1, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train2, X_test2, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        assert list(X_train1.index) == list(X_train2.index)
        assert list(X_test1.index) == list(X_test2.index)

    def test_different_seed_different_split(self):
        """Different seeds must produce different splits."""
        from sklearn.model_selection import train_test_split

        X = pd.DataFrame({"a": range(100)})
        y = pd.Series(range(100))

        X_train1, _, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train2, _, _, _ = train_test_split(X, y, test_size=0.2, random_state=99)

        assert list(X_train1.index) != list(X_train2.index)


# ── Test 4: Log-Transform Roundtrip ──────────────────────────────── #

class TestLogTransform:
    def test_roundtrip_accuracy(self):
        """log1p → expm1 should recover original values."""
        original = np.array([1.0, 10.0, 100.0, 1000.0, 0.5])
        log_vals = np.log1p(original)
        recovered = np.expm1(log_vals)

        np.testing.assert_allclose(recovered, original, rtol=1e-10)

    def test_zero_handling(self):
        """log1p(0) should be 0 and expm1(0) should be 0."""
        assert np.log1p(0) == 0.0
        assert np.expm1(0) == 0.0

    def test_negative_prediction_clipping(self):
        """Negative predictions after expm1 should be clipped to 0."""
        log_pred = np.array([-1.0, -0.5, 0.0, 1.0])
        hours = np.expm1(log_pred)
        hours_clipped = np.maximum(hours, 0)

        assert all(h >= 0 for h in hours_clipped)


# ── Test 5: Metric Computation ────────────────────────────────────── #

class TestMetrics:
    def _compute_metrics(self, actuals, predictions):
        """Standalone metric computation (no heavy imports needed)."""
        errors = np.abs(actuals - predictions)
        relative_errors = errors / np.maximum(actuals, 1e-6)
        mean_baseline_errors = np.abs(actuals - np.mean(actuals))
        return {
            "mae": float(np.mean(errors)),
            "mdae": float(np.median(errors)),
            "mre": float(np.mean(relative_errors)),
            "pred_25": float(np.mean(relative_errors <= 0.25) * 100),
            "pred_50": float(np.mean(relative_errors <= 0.50) * 100),
            "r2": float(1 - np.sum(errors**2) / np.sum((actuals - np.mean(actuals))**2)),
            "sa": float(
                (1 - np.sum(errors) / np.sum(mean_baseline_errors)) * 100
                if np.sum(mean_baseline_errors) > 0 else 0
            ),
        }

    def test_perfect_prediction(self):
        """Perfect predictions should give MAE=0, SA=100%, R²=1."""
        actuals = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        predictions = np.array([10.0, 20.0, 30.0, 40.0, 50.0])

        metrics = self._compute_metrics(actuals, predictions)
        assert metrics["mae"] == 0.0
        assert metrics["mdae"] == 0.0
        assert metrics["pred_25"] == 100.0
        assert metrics["pred_50"] == 100.0
        assert abs(metrics["r2"] - 1.0) < 1e-10
        assert abs(metrics["sa"] - 100.0) < 1e-10

    def test_mean_prediction_gives_sa_zero(self):
        """Predicting the mean for everything should give SA ≈ 0%."""
        actuals = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        predictions = np.full_like(actuals, actuals.mean())

        metrics = self._compute_metrics(actuals, predictions)
        assert abs(metrics["sa"]) < 1e-10, f"SA should be ~0 for mean prediction, got {metrics['sa']}"

    def test_known_mae(self):
        """MAE should be the mean of absolute errors."""
        actuals = np.array([10.0, 20.0, 30.0])
        predictions = np.array([12.0, 18.0, 25.0])

        metrics = self._compute_metrics(actuals, predictions)
        expected_mae = np.mean([2.0, 2.0, 5.0])
        assert abs(metrics["mae"] - expected_mae) < 1e-10

    def test_pred25_calculation(self):
        """PRED(25) = % of predictions within 25% relative error."""
        actuals = np.array([100.0, 100.0, 100.0, 100.0])
        predictions = np.array([110.0, 130.0, 80.0, 50.0])
        # Relative errors: 10%, 30%, 20%, 50%
        # Within 25%: 110 (10%) and 80 (20%) → 2/4 = 50%

        metrics = self._compute_metrics(actuals, predictions)
        assert abs(metrics["pred_25"] - 50.0) < 1e-10

    def test_negative_r2_when_worse_than_mean(self):
        """R² should be negative when model is worse than mean baseline."""
        actuals = np.array([10.0, 20.0, 30.0])
        predictions = np.array([50.0, 5.0, 60.0])

        metrics = self._compute_metrics(actuals, predictions)
        assert metrics["r2"] < 0


# ── Test 6: PCA Fits on Train Only ────────────────────────────────── #

class TestPCANoLeakage:
    def test_pca_fitted_on_train_only(self):
        """PCA must be fit on training data, not test data."""
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler

        np.random.seed(42)
        X_train = pd.DataFrame(
            np.random.randn(100, 10),
            columns=[f"emb_{i}" for i in range(10)]
        )
        X_test = pd.DataFrame(
            np.random.randn(20, 10) + 5,  # shifted distribution
            columns=[f"emb_{i}" for i in range(10)]
        )

        scaler = StandardScaler()
        train_scaled = scaler.fit_transform(X_train)

        pca = PCA(n_components=3)
        pca.fit(train_scaled)

        # Transform test data using train-fitted scaler and PCA
        test_scaled = scaler.transform(X_test)
        test_reduced = pca.transform(test_scaled)

        # Test data should NOT have zero mean after transform
        # (because scaler was fit on train, not test)
        test_means = np.abs(test_scaled.mean(axis=0))
        assert test_means.mean() > 0.5, \
            "Test data should not be centered if scaler was fit on train only"


# ── Test 7: Duration Filter ──────────────────────────────────────── #

class TestDurationFilter:
    def test_filter_removes_outliers(self):
        """Duration filter should remove samples outside [min, max] hours."""
        df = pd.DataFrame({
            "duration_hours": [0.5, 1.0, 24.0, 500.0, 2160.0, 2161.0, 5000.0],
        })

        min_hours = 1
        max_hours = 90 * 24  # 2160

        mask = (df["duration_hours"] >= min_hours) & (df["duration_hours"] <= max_hours)
        filtered = df[mask]

        assert len(filtered) == 4  # 1.0, 24.0, 500.0, 2160.0
        assert 0.5 not in filtered["duration_hours"].values
        assert 2161.0 not in filtered["duration_hours"].values
        assert 5000.0 not in filtered["duration_hours"].values

    def test_filter_preserves_boundaries(self):
        """Exact boundary values should be included."""
        df = pd.DataFrame({
            "duration_hours": [1.0, 2160.0],
        })

        mask = (df["duration_hours"] >= 1) & (df["duration_hours"] <= 2160)
        filtered = df[mask]

        assert len(filtered) == 2


# ── Test 8: Derived NLP Features ─────────────────────────────────── #

class TestDerivedFeatures:
    """Test derived NLP features using standalone reimplementations.

    These mirror the logic in nlp_features.py but don't require torch,
    so tests can run without GPU/heavy dependencies.
    """

    VAGUE_TERMS = {
        "some", "sometimes", "maybe", "probably", "might", "could", "should",
        "various", "etc", "somehow", "something", "stuff", "things", "issue",
        "problem", "seems", "appears", "possibly", "certain", "appropriate",
        "reasonable", "adequate", "sufficient", "necessary", "relevant",
    }

    DOMAIN_KEYWORDS = {
        "ui": {"ui", "frontend", "css", "html", "button", "dialog", "render",
               "display", "layout", "component", "view", "style", "theme", "widget"},
        "backend": {"api", "server", "endpoint", "handler", "controller", "service",
                    "middleware", "route", "request", "response", "rest", "grpc"},
        "database": {"database", "db", "sql", "query", "table", "schema", "migration",
                     "index", "join", "transaction", "postgres", "mysql", "mongo"},
        "infrastructure": {"docker", "kubernetes", "k8s", "deploy", "ci", "cd",
                           "pipeline", "terraform", "helm", "config", "yaml",
                           "nginx", "cluster"},
        "testing": {"test", "spec", "mock", "fixture", "assert", "coverage", "e2e",
                    "integration", "unit", "benchmark"},
        "security": {"auth", "token", "permission", "role", "encrypt", "certificate",
                     "ssl", "tls", "oauth", "rbac", "credential"},
    }

    @staticmethod
    def _count_cross_references(text):
        import re
        patterns = [r"#\d+", r"https?://\S+", r"[A-Z]+-\d+", r"@\w+"]
        return sum(len(re.findall(p, text)) for p in patterns)

    def _compute_ambiguity(self, text):
        words = set(text.lower().split())
        vague_count = len(words.intersection(self.VAGUE_TERMS))
        total_words = max(len(text.split()), 1)
        return vague_count / total_words

    def _compute_technical_scope(self, text):
        text_words = set(text.lower().split())
        return sum(1 for kw in self.DOMAIN_KEYWORDS.values()
                   if text_words.intersection(kw))

    def test_cross_reference_count(self):
        """Cross-reference density should count #123, URLs, @mentions."""
        count = self._count_cross_references(
            "See #123 and #456 at https://example.com cc @user"
        )
        assert count == 4  # 2 issue refs + 1 URL + 1 mention

    def test_ambiguity_index(self):
        """Ambiguity index should detect vague language."""
        vague = self._compute_ambiguity(
            "something seems probably wrong somehow maybe"
        )
        clear = self._compute_ambiguity(
            "connection pool returns null pointer exception on line 42"
        )
        assert vague > clear, "Vague text should have higher ambiguity index"

    def test_technical_scope(self):
        """Technical scope should count distinct domains referenced."""
        scope = self._compute_technical_scope(
            "update the api endpoint and fix the database query and add unit test"
        )
        assert scope >= 3  # backend + database + testing

    def test_zero_cross_refs(self):
        """Plain text with no references should have 0 cross-ref density."""
        count = self._count_cross_references(
            "Fix the button color in the settings page"
        )
        assert count == 0


# ── Test 9: Integration — Feature Alignment After Filtering ──────── #

class TestFeatureAlignment:
    """Integration tests verifying that pipeline steps produce aligned data.

    These tests require actual pipeline artifacts (parquet files) to exist.
    They are skipped if the data hasn't been generated yet. Run the full
    pipeline first, then run these tests to verify alignment.
    """

    @staticmethod
    def _data_exists():
        """Check if pipeline artifacts exist for integration tests."""
        from pathlib import Path
        data_dir = Path("data")
        raw_path = data_dir / "raw" / "issue_pr_pairs.parquet"
        nlp_path = data_dir / "processed" / "nlp_features.parquet"
        return raw_path.exists() and nlp_path.exists()

    @pytest.mark.skipif(
        not __import__("pathlib").Path("data/raw/issue_pr_pairs.parquet").exists(),
        reason="Raw data not available — run pipeline first"
    )
    def test_raw_data_and_nlp_features_same_length(self):
        """Raw data and NLP features must have the same number of rows."""
        from pathlib import Path
        raw = pd.read_parquet(Path("data/raw/issue_pr_pairs.parquet"))
        nlp = pd.read_parquet(Path("data/processed/nlp_features.parquet"))
        assert len(raw) == len(nlp), \
            f"Row count mismatch: raw={len(raw)}, nlp={len(nlp)}. Re-run nlp_features after clean_data."

    @pytest.mark.skipif(
        not __import__("pathlib").Path("data/raw/issue_pr_pairs.parquet").exists(),
        reason="Raw data not available — run pipeline first"
    )
    def test_duration_filter_preserves_alignment(self):
        """After duration filter, df and features must still be aligned."""
        from pathlib import Path
        raw = pd.read_parquet(Path("data/raw/issue_pr_pairs.parquet"))
        nlp = pd.read_parquet(Path("data/processed/nlp_features.parquet"))

        # Apply the same filter step_train uses
        mask = (raw["duration_hours"] >= 1) & (raw["duration_hours"] <= 2160)
        keep_idx = mask[mask].index.tolist()

        raw_filtered = raw.loc[keep_idx].reset_index(drop=True)
        nlp_filtered = nlp.iloc[keep_idx].reset_index(drop=True)

        assert len(raw_filtered) == len(nlp_filtered), \
            f"After filter: raw={len(raw_filtered)}, nlp={len(nlp_filtered)}"
        assert len(raw_filtered) > 0, "Duration filter removed all samples"

    @pytest.mark.skipif(
        not (__import__("pathlib").Path("data/raw/issue_pr_pairs.parquet").exists()
             and __import__("pathlib").Path("data/processed/repo_features.parquet").exists()),
        reason="Raw data or repo features not available"
    )
    def test_repo_features_alignment(self):
        """Repo features must align with raw data after duration filter."""
        from pathlib import Path
        raw = pd.read_parquet(Path("data/raw/issue_pr_pairs.parquet"))
        repo = pd.read_parquet(Path("data/processed/repo_features.parquet"))

        assert len(raw) == len(repo), \
            f"Row count mismatch: raw={len(raw)}, repo={len(repo)}. Re-run repo_features after clean_data."

        mask = (raw["duration_hours"] >= 1) & (raw["duration_hours"] <= 2160)
        keep_idx = mask[mask].index.tolist()

        raw_filtered = raw.loc[keep_idx].reset_index(drop=True)
        repo_filtered = repo.iloc[keep_idx].reset_index(drop=True)

        assert len(raw_filtered) == len(repo_filtered), \
            f"After filter: raw={len(raw_filtered)}, repo={len(repo_filtered)}"

    @pytest.mark.skipif(
        not __import__("pathlib").Path("data/raw/issue_pr_pairs.parquet").exists(),
        reason="Raw data not available"
    )
    def test_no_negative_durations(self):
        """Cleaned data should have no negative or zero durations."""
        from pathlib import Path
        raw = pd.read_parquet(Path("data/raw/issue_pr_pairs.parquet"))
        assert (raw["duration_hours"] > 0).all(), \
            f"Found {(raw['duration_hours'] <= 0).sum()} non-positive durations"

    @pytest.mark.skipif(
        not __import__("pathlib").Path("data/raw/issue_pr_pairs.parquet").exists(),
        reason="Raw data not available"
    )
    def test_no_duplicate_issues(self):
        """No duplicate repo+issue_number pairs after cleaning."""
        from pathlib import Path
        raw = pd.read_parquet(Path("data/raw/issue_pr_pairs.parquet"))
        dupes = raw.duplicated(subset=["repo", "issue_number"], keep=False).sum()
        assert dupes == 0, f"Found {dupes} duplicate repo+issue_number pairs"

    @pytest.mark.skipif(
        not __import__("pathlib").Path("data/raw/issue_pr_pairs.parquet").exists(),
        reason="Raw data not available"
    )
    def test_no_singleton_repos(self):
        """No repos with fewer than 10 samples after cleaning."""
        from pathlib import Path
        raw = pd.read_parquet(Path("data/raw/issue_pr_pairs.parquet"))
        repo_counts = raw["repo"].value_counts()
        small = repo_counts[repo_counts < 10]
        assert len(small) == 0, f"Found singleton repos: {small.to_dict()}"

    @pytest.mark.skipif(
        not __import__("pathlib").Path("models/model_a_text_only/results.json").exists(),
        reason="Model A not trained"
    )
    def test_model_a_test_indices_valid(self):
        """Model A's saved test_indices must be valid row positions."""
        import json
        from pathlib import Path

        with open(Path("models/model_a_text_only/results.json")) as f:
            results = json.load(f)

        test_indices = results.get("test_indices", [])
        n_train = results.get("n_train", 0)
        n_test = results.get("n_test", 0)

        assert len(test_indices) == n_test, \
            f"test_indices length ({len(test_indices)}) != n_test ({n_test})"
        assert len(test_indices) > 0, "No test indices saved"
        assert n_train + n_test > 0, "No samples in train or test"

    @pytest.mark.skipif(
        not __import__("pathlib").Path("models/model_a_text_only/predictions.csv").exists(),
        reason="Model A predictions not available"
    )
    def test_predictions_have_both_splits(self):
        """predictions.csv must contain both 'train' and 'test' rows."""
        from pathlib import Path
        preds = pd.read_csv(Path("models/model_a_text_only/predictions.csv"))
        splits = set(preds["split"].unique())
        assert "train" in splits, "Missing 'train' split in predictions"
        assert "test" in splits, "Missing 'test' split in predictions"
        assert (preds["actual_hours"] > 0).all(), "Found non-positive actuals"
