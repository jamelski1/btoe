"""Extract example predictions from each duration bucket.

For each model and each bucket (< 1 day, 1 day, 1-3 days, 3-7 days,
1-4 weeks, > 4 weeks), samples:
  - The best predictions (smallest relative error)
  - The worst predictions (largest relative error)

Joins predictions back to the raw issue-PR data so we can see the
actual text content that produced each prediction.

Output: models/<model>/analysis/example_predictions.md
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.config import get_data_dir, get_model_dir

logger = logging.getLogger(__name__)

BUCKETS = [
    (0, 8, "< 1 day"),
    (8, 24, "1 day"),
    (24, 72, "1-3 days"),
    (72, 168, "3-7 days"),
    (168, 720, "1-4 weeks"),
    (720, float("inf"), "> 4 weeks"),
]

MODELS = {
    "A": "model_a_text_only",
    "B": "model_b_repo_only",
    "C": "model_c_combined",
}


def _bucket_of(value):
    for low, high, label in BUCKETS:
        if low <= value < high:
            return label
    return BUCKETS[-1][2]


def _load_raw_data():
    data_dir = get_data_dir()
    parquet_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    csv_path = data_dir / "raw" / "issue_pr_pairs.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    return pd.read_csv(csv_path)


def _truncate(text, max_len=300):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r", "").replace("\n\n", "\n").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def _format_hours(h):
    """Pretty format hours → days/weeks."""
    if h < 1:
        return f"{int(h * 60)} min"
    if h < 24:
        return f"{h:.1f}h"
    d = h / 24
    if d < 14:
        return f"{d:.1f}d"
    return f"{d/7:.1f}w"


def extract_examples(model_key: str, n_per_bucket: int = 2):
    """For a trained model, extract good and bad predictions per bucket."""
    subdir = MODELS[model_key]
    model_dir = get_model_dir() / subdir

    preds_path = model_dir / "predictions.csv"
    results_path = model_dir / "results.json"
    if not preds_path.exists():
        logger.warning(f"No predictions.csv for model {model_key}")
        return None

    preds = pd.read_csv(preds_path)
    test_preds = preds[preds["split"] == "test"].reset_index(drop=True)

    # Load test indices to map back to the raw data
    test_indices = None
    if results_path.exists():
        with open(results_path) as f:
            results = json.load(f)
            test_indices = results.get("test_indices")

    if test_indices is None or len(test_indices) != len(test_preds):
        logger.warning(f"  Model {model_key}: can't map test rows back to source data")
        return None

    raw_df = _load_raw_data()
    # Apply duration filter the training would have applied
    config_max_hours = 90 * 24
    mask = (raw_df["duration_hours"] >= 1) & (raw_df["duration_hours"] <= config_max_hours)
    filtered_df = raw_df[mask].reset_index(drop=True)

    # Build joined dataframe
    test_preds["orig_idx"] = test_indices
    joined = test_preds.merge(
        filtered_df, left_on="orig_idx", right_index=True, how="left",
        suffixes=("", "_raw"),
    )
    joined["abs_error"] = (joined["actual_hours"] - joined["predicted_hours"]).abs()
    joined["rel_error"] = joined["abs_error"] / joined["actual_hours"].clip(lower=1e-6)
    joined["actual_bucket"] = joined["actual_hours"].apply(_bucket_of)
    joined["predicted_bucket"] = joined["predicted_hours"].apply(_bucket_of)

    return joined


def write_examples_markdown(model_key: str, joined: pd.DataFrame, n_per_bucket: int = 2):
    """Write a markdown report with examples per bucket."""
    subdir = MODELS[model_key]
    out_dir = get_model_dir() / subdir / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(f"# Example Predictions — Model {model_key} ({subdir})")
    lines.append("")
    lines.append(f"Test set: {len(joined)} samples")
    lines.append("")
    lines.append("For each actual-duration bucket, this report shows:")
    lines.append(f"- **{n_per_bucket} best predictions** (smallest relative error)")
    lines.append(f"- **{n_per_bucket} worst predictions** (largest relative error)")
    lines.append("")
    lines.append("---")
    lines.append("")

    for _, _, label in BUCKETS:
        bucket_df = joined[joined["actual_bucket"] == label]
        if len(bucket_df) == 0:
            continue

        lines.append(f"## Actual bucket: **{label}** ({len(bucket_df)} samples)")
        lines.append("")

        # Median stats for this bucket
        med_err = bucket_df["abs_error"].median()
        med_rel = bucket_df["rel_error"].median() * 100
        lines.append(f"*Median absolute error: {_format_hours(med_err)}, "
                      f"median relative error: {med_rel:.0f}%*")
        lines.append("")

        # Best predictions
        best = bucket_df.nsmallest(n_per_bucket, "rel_error")
        lines.append(f"### Best {n_per_bucket} predictions (most accurate)")
        lines.append("")
        for _, row in best.iterrows():
            _write_example_block(lines, row)

        # Worst predictions
        worst = bucket_df.nlargest(n_per_bucket, "rel_error")
        lines.append(f"### Worst {n_per_bucket} predictions (least accurate)")
        lines.append("")
        for _, row in worst.iterrows():
            _write_example_block(lines, row)

        lines.append("---")
        lines.append("")

    out_path = out_dir / "example_predictions.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"  Wrote {out_path}")
    return out_path


def _write_example_block(lines, row):
    """Append a single example entry to the markdown."""
    repo = row.get("repo", "?")
    issue_num = row.get("issue_number", "?")
    title = row.get("issue_title", "") or ""
    body = row.get("issue_body", "") or ""
    files = row.get("pr_files_changed", "") or ""

    n_files = len(str(files).split("|")) if files else 0

    lines.append(f"**{repo} #{issue_num}** — {title}")
    lines.append("")
    lines.append(f"- Actual: **{_format_hours(row['actual_hours'])}** "
                 f"({row['actual_hours']:.1f}h, bucket: {row['actual_bucket']})")
    lines.append(f"- Predicted: **{_format_hours(row['predicted_hours'])}** "
                 f"({row['predicted_hours']:.1f}h, bucket: {row['predicted_bucket']})")
    lines.append(f"- Error: {_format_hours(row['abs_error'])} "
                 f"({row['rel_error']*100:.0f}% off)")
    lines.append(f"- Files changed: {n_files}")
    lines.append("")
    if body:
        body_short = _truncate(body, 400)
        lines.append(f"> {body_short}")
        lines.append("")


def run_extract_examples(n_per_bucket: int = 2):
    """Extract examples for all trained canonical models."""
    for key in ["A", "B", "C"]:
        joined = extract_examples(key, n_per_bucket)
        if joined is None:
            continue
        logger.info(f"Model {key}: {len(joined)} test samples joined to source data")
        write_examples_markdown(key, joined, n_per_bucket)
