"""One-time patch: repair train_indices / test_indices in results.json files.

Background
----------
Before the fix in ``src/modeling/trainer.py`` (see TestIndexPreservation in
``tests/test_pipeline_correctness.py``), the embedding-reduction helpers
called ``reset_index(drop=True)`` on the already-split train and test
frames.  ``train_and_evaluate`` then stored ``X_train.index`` /
``X_test.index`` in results.json, so every model with PCA / Top-K / PLS on
embeddings recorded ``0..n_train-1`` and ``0..n_test-1`` instead of row
positions in the filtered dataset.  Metrics were unaffected (they are
computed from the y arrays), but SHAP and example-prediction steps that map
test rows back to the source data used the wrong rows.

What this script does
---------------------
For each affected results.json it:

1. Rebuilds the filtered dataset the run was trained on (min duration from
   config; max duration from the sensitivity cap in the folder name, or the
   config default of 90 days for all other runs).
2. Reproduces the ``train_test_split(test_size, random_state)`` the trainer
   used.
3. Verifies the split by checking that the actual durations at the rebuilt
   positions equal, in order, the train and test actuals saved in that
   folder's ``predictions.csv``.  A folder is patched only if this check
   passes.
4. Replaces ``train_indices`` and ``test_indices`` and nothing else.

Model B folders are skipped: Model B has no embedding reduction and stored
correct indices.  Folders whose data size matches no current filter (e.g.
``dim_sweep_*`` trained on an earlier dataset) are reported and left alone.

Usage:
    python src/experiments/patch_test_indices.py --dry-run
    python src/experiments/patch_test_indices.py
"""

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.utils.config import load_config  # noqa: E402

SKIP_PATTERNS = (
    re.compile(r"^model_b_"),
    re.compile(r"^sensitivity_b_"),
    re.compile(r"^llm_baseline"),
)
CAP_RE = re.compile(r"^sensitivity_[ac]_(\d+)d$")
NOCAP_RE = re.compile(r"^sensitivity_[ac]_no cap$")


def load_raw() -> pd.DataFrame:
    parquet_path = ROOT / "data" / "raw" / "issue_pr_pairs.parquet"
    csv_path = ROOT / "data" / "raw" / "issue_pr_pairs.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    raise FileNotFoundError("data/raw/issue_pr_pairs.{parquet,csv} not found")


def filtered_durations(df: pd.DataFrame, min_hours: float, max_hours: float) -> np.ndarray:
    mask = df["duration_hours"] >= min_hours
    if np.isfinite(max_hours):
        mask &= df["duration_hours"] <= max_hours
    return df.loc[mask, "duration_hours"].to_numpy()


def cap_hours_for(folder: str, default_max_hours: float) -> float:
    m = CAP_RE.match(folder)
    if m:
        return int(m.group(1)) * 24
    if NOCAP_RE.match(folder):
        return float("inf")
    return default_max_hours


def is_plain_range(idx) -> bool:
    idx = np.asarray(idx)
    return np.array_equal(idx, np.arange(len(idx)))


def main():
    parser = argparse.ArgumentParser(description="Repair stored train/test indices in results.json files")
    parser.add_argument("--models-dir", default=str(ROOT / "models"))
    parser.add_argument("--dry-run", action="store_true", help="Report what would change without writing")
    args = parser.parse_args()

    cfg = load_config()
    seed = cfg["modeling"]["random_seed"]
    test_size = cfg["modeling"]["test_size"]
    min_hours = cfg["filtering"]["min_duration_hours"]
    default_max_hours = cfg["filtering"]["max_duration_days"] * 24

    raw = load_raw()
    models_dir = Path(args.models_dir)

    patched, skipped, unpatchable, already_ok = [], [], [], []

    for results_path in sorted(models_dir.glob("*/results.json")):
        folder = results_path.parent.name
        if any(p.match(folder) for p in SKIP_PATTERNS):
            skipped.append(folder)
            continue

        with open(results_path) as f:
            results = json.load(f)
        if "train_indices" not in results or "test_indices" not in results:
            skipped.append(folder)
            continue

        n_train, n_test = len(results["train_indices"]), len(results["test_indices"])
        max_hours = cap_hours_for(folder, default_max_hours)
        y = filtered_durations(raw, min_hours, max_hours)

        if len(y) != n_train + n_test:
            unpatchable.append((folder, f"filtered rows {len(y)} != stored {n_train + n_test}"))
            continue

        train_idx, test_idx = train_test_split(np.arange(len(y)), test_size=test_size, random_state=seed)
        if len(train_idx) != n_train or len(test_idx) != n_test:
            unpatchable.append((folder, f"split sizes {len(train_idx)}/{len(test_idx)} != stored {n_train}/{n_test}"))
            continue

        # Verify against the saved predictions.csv actuals (train rows then test rows, split order)
        preds_path = results_path.parent / "predictions.csv"
        if not preds_path.exists():
            unpatchable.append((folder, "no predictions.csv to verify against"))
            continue
        preds = pd.read_csv(preds_path)
        train_act = preds.loc[preds["split"] == "train", "actual_hours"].to_numpy()
        test_act = preds.loc[preds["split"] == "test", "actual_hours"].to_numpy()
        if (len(train_act) != n_train or len(test_act) != n_test
                or not np.allclose(y[train_idx], train_act)
                or not np.allclose(y[test_idx], test_act)):
            unpatchable.append((folder, "rebuilt split does not reproduce predictions.csv actuals"))
            continue

        new_train = [int(i) for i in train_idx]
        new_test = [int(i) for i in test_idx]
        if results["train_indices"] == new_train and results["test_indices"] == new_test:
            already_ok.append(folder)
            continue

        was_plain = is_plain_range(results["train_indices"]) and is_plain_range(results["test_indices"])
        patched.append((folder, n_train, n_test, was_plain))
        if not args.dry_run:
            results["train_indices"] = new_train
            results["test_indices"] = new_test
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)

    verb = "Would patch" if args.dry_run else "Patched"
    print(f"{verb} {len(patched)} results.json file(s):")
    for folder, n_train, n_test, was_plain in patched:
        print(f"  {folder:45s} train={n_train} test={n_test} "
              f"{'(was plain 0..n range)' if was_plain else '(was other)'}")
    if already_ok:
        print(f"Already correct ({len(already_ok)}): {', '.join(already_ok)}")
    if skipped:
        print(f"Skipped by rule ({len(skipped)}): {', '.join(skipped)}")
    if unpatchable:
        print(f"Left untouched, could not verify ({len(unpatchable)}):")
        for folder, why in unpatchable:
            print(f"  {folder:45s} {why}")


if __name__ == "__main__":
    main()
