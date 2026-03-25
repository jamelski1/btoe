"""NLP feature extraction using CodeBERT embeddings.

Implements the SE3M approach:
1. Generate 768-dim CodeBERT embeddings for requirement texts
2. Derive interpretable features:
   - Semantic complexity score
   - Cross-reference density
   - Ambiguity index
   - Technical scope
"""

import logging
import re
from collections import Counter

import numpy as np
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer

from src.utils.config import load_config

logger = logging.getLogger(__name__)

# Technical domain keywords for scope detection
DOMAIN_KEYWORDS = {
    "ui": {"ui", "frontend", "css", "html", "button", "dialog", "render", "display",
           "layout", "component", "view", "style", "theme", "widget"},
    "backend": {"api", "server", "endpoint", "handler", "controller", "service",
                "middleware", "route", "request", "response", "rest", "grpc"},
    "database": {"database", "db", "sql", "query", "table", "schema", "migration",
                 "index", "join", "transaction", "postgres", "mysql", "mongo"},
    "infrastructure": {"docker", "kubernetes", "k8s", "deploy", "ci", "cd", "pipeline",
                       "terraform", "helm", "config", "yaml", "nginx", "cluster"},
    "testing": {"test", "spec", "mock", "fixture", "assert", "coverage", "e2e",
                "integration", "unit", "benchmark"},
    "security": {"auth", "token", "permission", "role", "encrypt", "certificate",
                 "ssl", "tls", "oauth", "rbac", "credential"},
}

# Ambiguity indicators
VAGUE_TERMS = {
    "some", "sometimes", "maybe", "probably", "might", "could", "should",
    "various", "etc", "somehow", "something", "stuff", "things", "issue",
    "problem", "seems", "appears", "possibly", "certain", "appropriate",
    "reasonable", "adequate", "sufficient", "necessary", "relevant",
}


class NLPFeatureExtractor:
    """Extracts NLP features from requirement texts using CodeBERT."""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        nlp_cfg = self.config["nlp"]
        self.model_name = nlp_cfg["model_name"]
        self.max_length = nlp_cfg["max_token_length"]
        self.batch_size = nlp_cfg["batch_size"]

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        self._tokenizer = None
        self._model = None

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            logger.info(f"Loading tokenizer: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return self._tokenizer

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading model: {self.model_name}")
            self._model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self._model.eval()
        return self._model

    def extract_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract all NLP features for a dataframe of issue-PR pairs.

        Args:
            df: DataFrame with columns 'issue_title', 'issue_body', 'pr_title', 'pr_body'

        Returns:
            DataFrame with embedding columns and derived feature columns
        """
        # Combine requirement text
        texts = (
            df["issue_title"].fillna("")
            + " "
            + df["issue_body"].fillna("")
            + " "
            + df["pr_title"].fillna("")
            + " "
            + df["pr_body"].fillna("")
        ).tolist()

        # Generate embeddings
        logger.info(f"Generating CodeBERT embeddings for {len(texts)} texts")
        embeddings = self._compute_embeddings(texts)

        # Build feature DataFrame
        emb_cols = [f"emb_{i}" for i in range(embeddings.shape[1])]
        emb_df = pd.DataFrame(embeddings, index=df.index, columns=emb_cols)

        # Compute derived features
        derived = pd.DataFrame(index=df.index)
        derived["complexity_score"] = self._compute_complexity_scores(embeddings)
        derived["cross_ref_density"] = texts_series_apply(texts, self._count_cross_references)
        derived["ambiguity_index"] = texts_series_apply(texts, self._compute_ambiguity)
        derived["technical_scope"] = texts_series_apply(texts, self._compute_technical_scope)
        derived["text_length"] = [len(t) for t in texts]
        derived["word_count"] = [len(t.split()) for t in texts]

        return pd.concat([emb_df, derived], axis=1)

    def _compute_embeddings(self, texts: list[str]) -> np.ndarray:
        """Compute CodeBERT [CLS] embeddings in batches."""
        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**encoded)
                # Use [CLS] token embedding
                cls_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                all_embeddings.append(cls_embeddings)

        return np.vstack(all_embeddings)

    def _compute_complexity_scores(self, embeddings: np.ndarray) -> np.ndarray:
        """Compute semantic complexity as cosine distance from centroid.

        Simple requirements cluster near the centroid; complex ones are farther away.
        """
        centroid = embeddings.mean(axis=0)
        # Cosine distance from centroid
        norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(centroid)
        norms = np.where(norms == 0, 1, norms)  # avoid division by zero
        similarities = (embeddings @ centroid) / norms
        return 1 - similarities  # distance = 1 - similarity

    @staticmethod
    def _count_cross_references(text: str) -> int:
        """Count references to other issues, PRs, URLs, or external systems."""
        patterns = [
            r"#\d+",                           # issue/PR references
            r"https?://\S+",                   # URLs
            r"[A-Z]+-\d+",                     # JIRA-style references
            r"@\w+",                           # user mentions
        ]
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text))
        return count

    @staticmethod
    def _compute_ambiguity(text: str) -> float:
        """Compute ambiguity index based on vague/uncertain language."""
        words = set(text.lower().split())
        vague_count = len(words.intersection(VAGUE_TERMS))
        total_words = max(len(text.split()), 1)
        return vague_count / total_words

    @staticmethod
    def _compute_technical_scope(text: str) -> int:
        """Count number of distinct technical domains referenced."""
        text_words = set(text.lower().split())
        domains_found = 0
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if text_words.intersection(keywords):
                domains_found += 1
        return domains_found


def texts_series_apply(texts: list[str], func) -> list:
    """Apply a function to each text in a list."""
    return [func(t) for t in texts]
