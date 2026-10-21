"""Leave-one-repository-out (LORO) evaluation for Models A and C.

Answers RQ4 (cross-project generalisation): for each of the five source
repositories, hold that repository out as the test set and train on the
other four.  Everything that is fitted (StandardScaler, PCA, XGBoost) is
fitted on the training repositories only.

Design decisions, matching the pooled pipeline in src/modeling/trainer.py:

* Data: data/raw/issue_pr_pairs.parquet with the 1h-90d duration filter
  (4,321 pairs), features from data/processed/nlp_features.parquet and
  data/processed/repo_features.parquet (row-aligned with the raw file).
* Model A = PCA-50 of the CodeBERT embeddings + 6 derived NLP features.
  Model C = Model A features + 13 repository features.  Column order is
  taken from each model's results.json ``feature_names``.
* Hyperparameters are frozen at ``best_params`` from each model's
  results.json.  There is no per-fold tuning.
* Target is log1p(duration_hours); predictions are expm1'd and clipped at 0.
* SA uses MAE_P0 from 1,000 random-guess draws (seed 42) sampled from the
  *training* repositories' actual durations (Shepperd & MacDonell, 2012),
  plus Glass's delta.  A constant-median predictor (median of training
  actuals) is reported as a second naive baseline.
* Model A vs Model C per fold: Wilcoxon signed-rank test on paired absolute
  errors (two-sided).
* A pooled 80/20 sanity check (seed 42) with the same code path must
  reproduce Model A's published MAE / SA before the LORO numbers are
  trusted.

Outputs: models/loro_results.csv (one row per held-out repo) and
models/loro_results.json (per-fold rows, cross-fold summary, pooled check,
settings).

Usage:
    python src/experiments/loro_eval.py
    python src/experiments/loro_eval.py --models A C --out-dir models
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.utils.config import load_config  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL_DIRS = {"A": "model_a_text_only", "C": "model_c_combined"}
N_RUNS = 1000


# ---------------------------------------------------------------------------
# Metrics (mirrors ModelTrainer.compute_metrics / _compute_sa)
# ---------------------------------------------------------------------------
def random_baseline(test_actuals, train_actuals, seed, n_runs=N_RUNS):
    rng = np.random.RandomState(seed)
    maes = []
    for _ in range(n_runs):
        guess = rng.choice(train_actuals, size=len(test_actuals), replace=True)
        maes.append(float(np.mean(np.abs(test_actuals - guess))))
    return float(np.mean(maes)), float(np.std(maes, ddof=1))


def metrics(actuals, preds, mae_p0, std_p0):
    err = np.abs(actuals - preds)
    rel = err / np.maximum(actuals, 1e-6)
    mae = float(np.mean(err))
    return {
        "mae": mae,
        "mdae": float(np.median(err)),
        "mre": float(np.mean(rel)),
        "pred_25": float(np.mean(rel <= 0.25) * 100),
        "pred_50": float(np.mean(rel <= 0.50) * 100),
        "r2": float(1 - np.sum((actuals - preds) ** 2) / np.sum((actuals - np.mean(actuals)) ** 2)),
        "sa": float((1 - mae / mae_p0) * 100) if mae_p0 > 0 else 0.0,
        "glass_delta": float((mae_p0 - mae) / std_p0) if std_p0 > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# Feature construction
# ---------------------------------------------------------------------------
def load_data(cfg):
    raw = pd.read_parquet(ROOT / "data" / "raw" / "issue_pr_pairs.parquet")
    nlp = pd.read_parquet(ROOT / "data" / "processed" / "nlp_features.parquet")
    repo = pd.read_parquet(ROOT / "data" / "processed" / "repo_features.parquet")
    if not (len(raw) == len(nlp) == len(repo)):
        raise RuntimeError(f"Row mismatch: raw={len(raw)} nlp={len(nlp)} repo={len(repo)}")

    min_h = cfg["filtering"]["min_duration_hours"]
    max_h = cfg["filtering"]["max_duration_days"] * 24
    mask = ((raw["duration_hours"] >= min_h) & (raw["duration_hours"] <= max_h)).to_numpy()

    raw = raw[mask].reset_index(drop=True)
    nlp = nlp[mask].reset_index(drop=True)
    repo = repo[mask].reset_index(drop=True)
    logger.info(f"Filtered dataset: {len(raw)} pairs, {raw['repo'].nunique()} repos")
    return raw, nlp, repo


def build_features(nlp_tr, nlp_te, extra_tr, extra_te, feature_names, n_components, seed):
    """Fit scaler+PCA on the training embeddings only; return ordered frames."""
    emb_cols = [c for c in nlp_tr.columns if c.startswith("emb_")]
    derived_cols = [c for c in nlp_tr.columns if not c.startswith("emb_")]
    n_components = min(n_components, len(nlp_tr) // 5, len(emb_cols))

    scaler = StandardScaler().fit(nlp_tr[emb_cols])
    pca = PCA(n_components=n_components, random_state=seed).fit(scaler.transform(nlp_tr[emb_cols]))
    pca_cols = [f"pca_{i}" for i in range(n_components)]

    def assemble(nlp_part, extra_part):
        red = pca.transform(scaler.transform(nlp_part[emb_cols]))
        parts = [pd.DataFrame(red, columns=pca_cols, index=nlp_part.index),
                 nlp_part[derived_cols]]
        if extra_part is not None:
            parts.append(extra_part)
        X = pd.concat(parts, axis=1)
        missing = [c for c in feature_names if c not in X.columns]
        if missing:
            raise RuntimeError(f"Missing features: {missing[:5]}")
        return X[feature_names]

    return assemble(nlp_tr, extra_tr), assemble(nlp_te, extra_te), float(pca.explained_variance_ratio_.sum())


def fit_predict(X_tr, y_tr, X_te, params, seed):
    model = XGBRegressor(objective="reg:squarederror", random_state=seed, n_jobs=-1, **params)
    model.fit(X_tr, np.log1p(y_tr))
    return np.maximum(np.expm1(model.predict(X_te)), 0)


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Leave-one-repository-out evaluation")
    parser.add_argument("--models", nargs="+", default=["A", "C"], choices=list(MODEL_DIRS))
    parser.add_argument("--out-dir", default=str(ROOT / "models"))
    parser.add_argument("--skip-pooled-check", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    seed = cfg["modeling"]["random_seed"]
    test_size = cfg["modeling"]["test_size"]
    n_components = cfg.get("pca", {}).get("n_components", 50)

    specs = {}
    for key in args.models:
        with open(ROOT / "models" / MODEL_DIRS[key] / "results.json") as f:
            r = json.load(f)
        specs[key] = {"params": r["best_params"], "feature_names": r["feature_names"],
                      "published": r["test_metrics"]}
        logger.info(f"Model {key}: {len(r['feature_names'])} features, params frozen from "
                    f"{MODEL_DIRS[key]}/results.json")

    raw, nlp, repo = load_data(cfg)
    y_all = raw["duration_hours"].to_numpy(dtype=float)
    repos = sorted(raw["repo"].unique())

    # ---- Pooled 80/20 sanity check -------------------------------------
    pooled = {}
    if not args.skip_pooled_check:
        tr_idx, te_idx = train_test_split(np.arange(len(raw)), test_size=test_size, random_state=seed)
        mae_p0, std_p0 = random_baseline(y_all[te_idx], y_all[tr_idx], seed)
        for key, spec in specs.items():
            extra_tr = repo.iloc[tr_idx] if key == "C" else None
            extra_te = repo.iloc[te_idx] if key == "C" else None
            X_tr, X_te, _ = build_features(nlp.iloc[tr_idx], nlp.iloc[te_idx], extra_tr, extra_te,
                                           spec["feature_names"], n_components, seed)
            preds = fit_predict(X_tr, y_all[tr_idx], X_te, spec["params"], seed)
            m = metrics(y_all[te_idx], preds, mae_p0, std_p0)
            pub = spec["published"]
            pooled[key] = {"n_test": int(len(te_idx)), "mae": m["mae"], "sa": m["sa"], "mae_p0": mae_p0,
                           "published_mae": pub["mae"], "published_sa": pub["sa"],
                           "published_mae_p0": pub.get("mae_p0")}
            logger.info(f"Pooled check Model {key}: MAE={m['mae']:.2f} (published {pub['mae']:.2f}) "
                        f"SA={m['sa']:.2f} (published {pub['sa']:.2f}) MAE_P0={mae_p0:.2f}")

    # ---- LORO folds ------------------------------------------------------
    rows = []
    for held_out in repos:
        te = np.where(raw["repo"].to_numpy() == held_out)[0]
        tr = np.where(raw["repo"].to_numpy() != held_out)[0]
        y_tr, y_te = y_all[tr], y_all[te]
        t0 = time.time()

        mae_p0, std_p0 = random_baseline(y_te, y_tr, seed)
        median_pred = float(np.median(y_tr))
        median_mae = float(np.mean(np.abs(y_te - median_pred)))

        row = {"held_out_repo": held_out, "n_test": int(len(te)), "n_train": int(len(tr)),
               "mae_p0": mae_p0, "std_p0": std_p0,
               "median_predictor_hours": median_pred, "median_predictor_mae": median_mae,
               "median_predictor_sa": float((1 - median_mae / mae_p0) * 100)}
        abs_err = {}
        for key, spec in specs.items():
            extra_tr = repo.iloc[tr] if key == "C" else None
            extra_te = repo.iloc[te] if key == "C" else None
            X_tr, X_te, var = build_features(nlp.iloc[tr], nlp.iloc[te], extra_tr, extra_te,
                                             spec["feature_names"], n_components, seed)
            preds = fit_predict(X_tr, y_tr, X_te, spec["params"], seed)
            m = metrics(y_te, preds, mae_p0, std_p0)
            abs_err[key] = np.abs(y_te - preds)
            for k, v in m.items():
                row[f"{k}_{key}"] = v
            row[f"pca_variance_{key}"] = var
            row[f"gain_over_median_{key}"] = median_mae - m["mae"]

        if "A" in abs_err and "C" in abs_err:
            stat, p = wilcoxon(abs_err["A"], abs_err["C"])
            row["wilcoxon_A_vs_C_stat"] = float(stat)
            row["wilcoxon_A_vs_C_p"] = float(p)
        row["fold_seconds"] = round(time.time() - t0, 1)
        rows.append(row)
        logger.info(f"LORO {held_out:22s} n_test={len(te):4d} "
                    + " ".join(f"MAE_{k}={row[f'mae_{k}']:.1f} SA_{k}={row[f'sa_{k}']:.1f}" for k in specs)
                    + f" median_MAE={median_mae:.1f} MAE_P0={mae_p0:.1f}"
                    + (f" p={row['wilcoxon_A_vs_C_p']:.3g}" if "wilcoxon_A_vs_C_p" in row else ""))

    df = pd.DataFrame(rows)
    summary = {}
    for key in specs:
        summary[f"sa_{key}_mean"] = float(df[f"sa_{key}"].mean())
        summary[f"sa_{key}_sd"] = float(df[f"sa_{key}"].std(ddof=1))
        summary[f"mae_{key}_mean"] = float(df[f"mae_{key}"].mean())
        summary[f"gain_over_median_{key}_mean"] = float(df[f"gain_over_median_{key}"].mean())
        summary[f"gain_over_median_{key}_min"] = float(df[f"gain_over_median_{key}"].min())
        summary[f"gain_over_median_{key}_max"] = float(df[f"gain_over_median_{key}"].max())
    summary["median_predictor_sa_mean"] = float(df["median_predictor_sa"].mean())
    summary["n_pairs_total"] = int(len(raw))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "loro_results.csv", index=False)
    with open(out_dir / "loro_results.json", "w") as f:
        json.dump({
            "description": "Leave-one-repository-out evaluation, Models A and C, frozen hyperparameters",
            "settings": {"seed": seed, "n_random_runs": N_RUNS, "pca_n_components": n_components,
                         "duration_filter_hours": [cfg["filtering"]["min_duration_hours"],
                                                   cfg["filtering"]["max_duration_days"] * 24],
                         "hyperparameters": {k: specs[k]["params"] for k in specs},
                         "features": {k: len(specs[k]["feature_names"]) for k in specs}},
            "pooled_check": pooled,
            "folds": rows,
            "summary": summary,
        }, f, indent=2)
    logger.info(f"Saved {out_dir / 'loro_results.csv'} and {out_dir / 'loro_results.json'}")

    # ---- Console table ---------------------------------------------------
    print()
    print("=" * 100)
    print(f"LEAVE-ONE-REPOSITORY-OUT ({len(raw)} pairs, {len(repos)} folds)")
    print("=" * 100)
    cols = (["held_out_repo", "n_test"] + [f"mae_{k}" for k in specs] + ["median_predictor_mae"]
            + [f"sa_{k}" for k in specs] + ["median_predictor_sa"]
            + (["wilcoxon_A_vs_C_p"] if "wilcoxon_A_vs_C_p" in df else []))
    print(df[cols].to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print()
    for key in specs:
        print(f"Model {key}: SA mean={summary[f'sa_{key}_mean']:.2f} SD={summary[f'sa_{key}_sd']:.2f}; "
              f"mean gain over median predictor={summary[f'gain_over_median_{key}_mean']:.1f}h "
              f"(min {summary[f'gain_over_median_{key}_min']:.1f}h, max {summary[f'gain_over_median_{key}_max']:.1f}h)")
    if pooled:
        for key, p in pooled.items():
            print(f"Pooled check Model {key}: MAE {p['mae']:.2f} vs published {p['published_mae']:.2f}; "
                  f"SA {p['sa']:.2f} vs published {p['published_sa']:.2f}")


if __name__ == "__main__":
    main()
