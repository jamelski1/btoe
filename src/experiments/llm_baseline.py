"""Zero-shot LLM baseline for effort estimation.

Sends raw issue text to a frontier LLM (GPT-4o / GPT-5.2 / etc.) and
asks it to predict implementation duration in hours. Compares against
actual durations and our trained Model A predictions.

By default, evaluates on the exact same test samples as Model A
(loaded from models/model_a_text_only/results.json test_indices)
for a fair head-to-head comparison.

Supports resume: if interrupted, re-running with the same arguments
will load partial results and continue from where it stopped.

Usage:
    pip install openai
    set OPENAI_API_KEY=sk-...
    python src/experiments/llm_baseline.py --model gpt-4o
    python src/experiments/llm_baseline.py --model gpt-5.2
    python src/experiments/llm_baseline.py --n 50 --random   # random subset instead

Output: models/llm_baseline/<model>/results.json + comparison table
"""

import argparse
import json
import logging
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a senior software engineer estimating how long a GitHub issue will take to resolve.

Given an issue title and description from an open-source project, estimate the implementation duration in hours — from when a developer is assigned to when the pull request is merged.

Consider:
- Complexity of the described task
- Number of files likely to be changed
- Whether it's a bug fix, feature, refactor, or documentation
- Typical open-source contribution patterns

Respond with ONLY a JSON object in this exact format:
{"hours": <number>, "reasoning": "<one sentence>"}

Do not include any other text outside the JSON."""


def estimate_with_llm(title: str, body: str, model: str = "gpt-4o") -> tuple[float | None, str]:
    """Send issue text to an LLM and parse the estimated hours."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("pip install openai")

    client = OpenAI()

    body_truncated = body[:2000] if body else ""
    user_msg = f"Issue Title: {title}\n\nIssue Body:\n{body_truncated}"

    try:
        token_param = "max_completion_tokens" if "5" in model or "o3" in model or "o4" in model else "max_tokens"
        api_kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.0,
            token_param: 200,
        }

        response = client.chat.completions.create(**api_kwargs)

        text = response.choices[0].message.content.strip()

        json_match = re.search(r'\{[^}]+\}', text)
        if json_match:
            parsed = json.loads(json_match.group())
            hours = float(parsed.get("hours", 0))
            reasoning = parsed.get("reasoning", "")
            return hours, reasoning
        else:
            logger.warning(f"  Could not parse JSON from: {text[:100]}")
            return None, f"Parse error: {text[:100]}"

    except Exception as e:
        logger.warning(f"  API error: {e}")
        return None, str(e)


def compute_metrics(actuals: np.ndarray, predictions: np.ndarray) -> dict:
    """Compute the same metrics as our XGBoost pipeline."""
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


def load_model_a_test_set() -> tuple[list[int], pd.DataFrame] | None:
    """Load Model A's test indices and return (indices, filtered_df)."""
    results_path = Path("models/model_a_text_only/results.json")
    if not results_path.exists():
        return None

    with open(results_path) as f:
        results = json.load(f)

    test_indices = results.get("test_indices")
    if not test_indices:
        return None

    # Load and filter raw data the same way training does
    data_dir = Path("data")
    parquet_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    csv_path = data_dir / "raw" / "issue_pr_pairs.csv"

    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        return None

    mask = (df["duration_hours"] >= 1) & (df["duration_hours"] <= 2160)
    df = df[mask].reset_index(drop=True)

    return test_indices, df


def main():
    parser = argparse.ArgumentParser(description="LLM Zero-Shot Effort Estimation Baseline")
    parser.add_argument("--model", default="gpt-4o",
                        help="OpenAI model name (default: gpt-4o)")
    parser.add_argument("--n", type=int, default=None,
                        help="Limit to first N test samples (default: all)")
    parser.add_argument("--random", action="store_true",
                        help="Use random sampling instead of Model A's test set")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (only used with --random)")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY environment variable first:")
        print("  set OPENAI_API_KEY=sk-...")
        return

    # Output directory per model
    model_slug = args.model.replace("/", "_").replace(".", "_")
    out_dir = Path("models/llm_baseline") / model_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    partial_path = out_dir / "partial_results.json"

    # Load data
    if args.random:
        # Random sampling mode (original behavior)
        data_dir = Path("data")
        if (data_dir / "raw" / "issue_pr_pairs.parquet").exists():
            df = pd.read_parquet(data_dir / "raw" / "issue_pr_pairs.parquet")
        else:
            df = pd.read_csv(data_dir / "raw" / "issue_pr_pairs.csv")
        mask = (df["duration_hours"] >= 1) & (df["duration_hours"] <= 2160)
        df = df[mask].reset_index(drop=True)
        n = args.n or 100
        sample = df.sample(n=min(n, len(df)), random_state=args.seed)
        logger.info(f"Random sampling: {len(sample)} issues")
    else:
        # Match Model A's test set (default)
        loaded = load_model_a_test_set()
        if loaded is None:
            print("Could not load Model A test indices.")
            print("Either train Model A first, or use --random for random sampling.")
            return

        test_indices, df = loaded
        sample = df.iloc[test_indices].reset_index(drop=True)
        if args.n:
            sample = sample.head(args.n)
        logger.info(f"Using Model A's test set: {len(sample)} samples (same split, same data)")

    logger.info(f"Using model: {args.model}")
    logger.info(f"Duration range: {sample['duration_hours'].min():.1f}h - {sample['duration_hours'].max():.1f}h")

    # Load partial results for resume
    completed = {}
    if partial_path.exists():
        try:
            with open(partial_path) as f:
                partial = json.load(f)
            for r in partial:
                key = f"{r['repo']}#{r['issue_number']}"
                if r.get("predicted_hours") is not None:
                    completed[key] = r
            logger.info(f"Resuming: {len(completed)} predictions already completed")
        except Exception:
            pass

    # Run predictions
    results = []
    new_predictions = 0
    for i, (idx, row) in enumerate(sample.iterrows()):
        title = row.get("issue_title", "") or ""
        body = row.get("issue_body", "") or ""
        actual = row["duration_hours"]
        repo = row.get("repo", "?")
        issue_num = row.get("issue_number", "?")
        key = f"{repo}#{issue_num}"

        # Skip if already completed (resume support)
        if key in completed:
            results.append(completed[key])
            continue

        logger.info(f"  [{i+1}/{len(sample)}] {key} (actual: {actual:.1f}h)")

        hours, reasoning = estimate_with_llm(title, body, model=args.model)

        if hours is not None:
            error = abs(actual - hours)
            rel_error = error / max(actual, 1e-6)
            logger.info(f"    Predicted: {hours:.1f}h, Error: {error:.1f}h ({rel_error*100:.0f}%)")
        else:
            logger.info(f"    Failed: {reasoning}")

        result_row = {
            "repo": repo,
            "issue_number": int(issue_num) if issue_num != "?" else 0,
            "issue_title": title[:100],
            "actual_hours": actual,
            "predicted_hours": hours,
            "reasoning": reasoning,
        }
        results.append(result_row)
        new_predictions += 1

        # Save partial results every 25 predictions
        if new_predictions % 25 == 0:
            with open(partial_path, "w") as f:
                json.dump(results, f)
            logger.info(f"  Checkpoint: {len(results)} total ({new_predictions} new)")

        # Rate limiting
        if i < len(sample) - 1:
            time.sleep(0.3)

    # Final save of partial results
    with open(partial_path, "w") as f:
        json.dump(results, f)

    # Filter successful predictions
    results_df = pd.DataFrame(results)
    valid = results_df.dropna(subset=["predicted_hours"])
    failed = len(results_df) - len(valid)

    if len(valid) == 0:
        print("No valid predictions. Check API key and model name.")
        return

    logger.info(f"\n{len(valid)} successful predictions, {failed} failures")

    # Compute metrics
    actuals = valid["actual_hours"].values
    predictions = valid["predicted_hours"].values
    metrics = compute_metrics(actuals, predictions)

    # Print results
    print()
    print("=" * 70)
    print(f"LLM ZERO-SHOT BASELINE ({args.model}, n={len(valid)})")
    if not args.random:
        print(f"  Evaluated on Model A's exact test set for fair comparison")
    print("=" * 70)
    print(f"  MAE:      {metrics['mae']:.2f}h")
    print(f"  MdAE:     {metrics['mdae']:.2f}h")
    print(f"  Mean MRE: {metrics['mre']:.2%}")
    print(f"  PRED(25): {metrics['pred_25']:.1f}%")
    print(f"  PRED(50): {metrics['pred_50']:.1f}%")
    print(f"  R²:       {metrics['r2']:.4f}")
    print(f"  SA:       {metrics['sa']:.1f}%")
    print()

    # Compare with Model A predictions on the same samples
    model_a_preds_path = Path("models/model_a_text_only/predictions.csv")
    model_a_results_path = Path("models/model_a_text_only/results.json")

    if model_a_results_path.exists():
        with open(model_a_results_path) as f:
            model_a_meta = json.load(f)
        model_a_metrics = model_a_meta.get("test_metrics", {})

        if model_a_metrics:
            print(f"{'='*70}")
            print("HEAD-TO-HEAD: LLM vs Model A (same test samples)")
            print(f"{'='*70}")
            print(f"  {'Metric':<12} {'LLM':>12} {'Model A':>12} {'Winner':>12}")
            print(f"  {'-'*50}")
            comparisons = [
                ("MAE", "mae", True),     # lower is better
                ("MdAE", "mdae", True),
                ("PRED(25)", "pred_25", False),  # higher is better
                ("PRED(50)", "pred_50", False),
                ("SA", "sa", False),
                ("R²", "r2", False),
            ]
            for label, key, lower_better in comparisons:
                llm_val = metrics.get(key, 0)
                ma_val = model_a_meta.get("test_metrics", {}).get(key, 0)
                if lower_better:
                    winner = "LLM" if llm_val < ma_val else "Model A"
                else:
                    winner = "LLM" if llm_val > ma_val else "Model A"
                print(f"  {label:<12} {llm_val:>12.2f} {ma_val:>12.2f} {winner:>12}")
            print()

    # Save final results
    final = {
        "model": args.model,
        "n_samples": len(valid),
        "n_failed": failed,
        "matched_model_a_test_set": not args.random,
        "metrics": metrics,
    }
    with open(out_dir / "results.json", "w") as f:
        json.dump(final, f, indent=2)

    results_df.to_csv(out_dir / "predictions.csv", index=False)
    logger.info(f"Results saved to {out_dir}")


if __name__ == "__main__":
    main()
