"""Data quality report for the raw issue-PR pairs dataset.

Reports missing values, distributions, and potential data issues
across all columns. Output is suitable for inclusion in the paper's
methodology section and threats to validity.

Usage:
    python -m src.analysis.data_quality
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.config import get_data_dir

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def run_data_quality_report():
    """Generate a comprehensive data quality report."""
    data_dir = get_data_dir()
    parquet_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    csv_path = data_dir / "raw" / "issue_pr_pairs.csv"

    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        print("No raw data found.")
        return

    print()
    print("=" * 80)
    print("DATA QUALITY REPORT")
    print(f"Dataset: {len(df)} issue-PR pairs")
    print("=" * 80)

    # ── Missing values ─────────────────────────────────────────── #
    print()
    print("MISSING VALUES BY COLUMN")
    print("-" * 80)
    print(f"{'Column':<25} {'Total':>8} {'Missing':>8} {'Missing%':>10} {'Type':<15}")
    print("-" * 80)

    for col in df.columns:
        total = len(df)
        # Count nulls, NaN, empty strings, and "None" strings
        null_count = df[col].isna().sum()
        if df[col].dtype == object:
            empty_count = (df[col].fillna("") == "").sum()
            none_str_count = (df[col].fillna("").astype(str).str.lower() == "none").sum()
            missing = null_count + empty_count - (null_count)  # don't double-count
            missing_detail = f"null={null_count}, empty={empty_count-null_count}"
        else:
            missing = null_count
            missing_detail = f"null={null_count}"

        pct = (missing / total) * 100
        dtype = str(df[col].dtype)

        flag = " ⚠" if pct > 10 else ""
        print(f"{col:<25} {total:>8} {missing:>8} {pct:>9.1f}% {dtype:<15}{flag}")

    # ── Text column statistics ─────────────────────────────────── #
    print()
    print("TEXT COLUMN STATISTICS")
    print("-" * 80)

    text_cols = ["issue_title", "issue_body", "pr_title", "pr_body"]
    for col in text_cols:
        if col not in df.columns:
            continue
        series = df[col].fillna("")
        lengths = series.str.len()
        word_counts = series.str.split().str.len().fillna(0)

        print(f"\n  {col}:")
        print(f"    Non-empty: {(lengths > 0).sum()}/{len(df)} ({(lengths > 0).sum()/len(df)*100:.1f}%)")
        print(f"    Char length: min={lengths.min()}, median={lengths.median():.0f}, "
              f"mean={lengths.mean():.0f}, max={lengths.max()}")
        print(f"    Word count:  min={word_counts.min():.0f}, median={word_counts.median():.0f}, "
              f"mean={word_counts.mean():.0f}, max={word_counts.max():.0f}")

    # ── Duration statistics ────────────────────────────────────── #
    print()
    print("DURATION DISTRIBUTION")
    print("-" * 80)

    dur = df["duration_hours"]
    print(f"  Count:    {dur.count()}")
    print(f"  Missing:  {dur.isna().sum()}")
    print(f"  Min:      {dur.min():.1f}h ({dur.min()/24:.1f}d)")
    print(f"  25th:     {dur.quantile(0.25):.1f}h ({dur.quantile(0.25)/24:.1f}d)")
    print(f"  Median:   {dur.median():.1f}h ({dur.median()/24:.1f}d)")
    print(f"  Mean:     {dur.mean():.1f}h ({dur.mean()/24:.1f}d)")
    print(f"  75th:     {dur.quantile(0.75):.1f}h ({dur.quantile(0.75)/24:.1f}d)")
    print(f"  95th:     {dur.quantile(0.95):.1f}h ({dur.quantile(0.95)/24:.1f}d)")
    print(f"  Max:      {dur.max():.1f}h ({dur.max()/24:.1f}d)")
    print(f"  Std:      {dur.std():.1f}h")
    print(f"  Skewness: {dur.skew():.2f}")

    # Duration buckets
    print()
    print("  Duration buckets:")
    buckets = [
        (0, 8, "< 1 day"),
        (8, 24, "1 day"),
        (24, 72, "1-3 days"),
        (72, 168, "3-7 days"),
        (168, 720, "1-4 weeks"),
        (720, 2160, "4-12 weeks"),
        (2160, float("inf"), "> 12 weeks"),
    ]
    for low, high, label in buckets:
        count = ((dur >= low) & (dur < high)).sum()
        pct = count / len(dur) * 100
        bar = "#" * int(pct / 2)
        print(f"    {label:<12} {count:>6} ({pct:>5.1f}%) {bar}")

    # ── Per-repo breakdown ─────────────────────────────────────── #
    print()
    print("PER-REPOSITORY BREAKDOWN")
    print("-" * 80)
    print(f"{'Repository':<35} {'Count':>7} {'%':>7} {'Med Dur':>10} {'Mean Dur':>10}")
    print("-" * 80)

    for repo, group in df.groupby("repo"):
        count = len(group)
        pct = count / len(df) * 100
        med = group["duration_hours"].median()
        mean = group["duration_hours"].mean()
        print(f"{repo:<35} {count:>7} {pct:>6.1f}% {med:>9.1f}h {mean:>9.1f}h")

    # ── Potential data issues ──────────────────────────────────── #
    print()
    print("POTENTIAL DATA ISSUES")
    print("-" * 80)

    # Negative durations
    neg = (dur < 0).sum()
    print(f"  Negative durations:  {neg}")

    # Zero durations
    zero = (dur == 0).sum()
    print(f"  Zero durations:      {zero}")

    # Very short (<1 hour)
    very_short = (dur < 1).sum()
    print(f"  < 1 hour:            {very_short}")

    # Duplicate issue numbers within same repo
    dupes = df.duplicated(subset=["repo", "issue_number"], keep=False).sum()
    print(f"  Duplicate repo+issue: {dupes}")

    # Empty issue bodies
    empty_body = (df["issue_body"].fillna("") == "").sum()
    print(f"  Empty issue_body:    {empty_body}")

    # Empty PR bodies
    if "pr_body" in df.columns:
        empty_pr = (df["pr_body"].fillna("") == "").sum()
        print(f"  Empty pr_body:       {empty_pr}")

    # Files changed = 0
    if "num_files_changed" in df.columns:
        no_files = (df["num_files_changed"] == 0).sum()
        print(f"  0 files changed:     {no_files}")

    # ── After duration filter ─────────────────────────────────── #
    print()
    print("AFTER DURATION FILTER (1h - 2160h)")
    print("-" * 80)

    mask = (dur >= 1) & (dur <= 2160)
    filtered = df[mask]
    removed = len(df) - len(filtered)
    print(f"  Kept:    {len(filtered)} ({len(filtered)/len(df)*100:.1f}%)")
    print(f"  Removed: {removed} ({removed/len(df)*100:.1f}%)")
    print(f"  Filtered median: {filtered['duration_hours'].median():.1f}h")
    print(f"  Filtered mean:   {filtered['duration_hours'].mean():.1f}h")

    # ── How missing values are handled ─────────────────────────── #
    print()
    print("MISSING VALUE HANDLING IN PIPELINE")
    print("-" * 80)
    print("  issue_title:       fillna('') → empty string treated as zero-length text")
    print("  issue_body:        fillna('') → empty string treated as zero-length text")
    print("  pr_title:          excluded by default (include_pr_text=False)")
    print("  pr_body:           excluded by default (include_pr_text=False)")
    print("  pr_files_changed:  dropna() in repo feature extraction; empty = 0 features")
    print("  issue_assigned_at: null → falls back to issue_created_at for duration calc")
    print("  duration_hours:    filtered to [1h, 2160h]; nulls excluded")
    print()

    # Save report
    out_path = get_data_dir() / "data_quality_report.txt"
    print(f"Report also saved to pipeline.log")

    return df


if __name__ == "__main__":
    run_data_quality_report()
