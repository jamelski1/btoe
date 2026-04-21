"""Zero-shot LLM baseline for effort estimation.

Sends raw issue text to a frontier LLM (GPT-4o / GPT-5.2 / etc.) and
asks it to predict implementation duration in hours. Compares against
actual durations and our trained Model A predictions.

This is a "black box" baseline — the LLM sees only the issue title and
body, with no training, no embeddings, and no feature engineering.

Usage:
    pip install openai
    set OPENAI_API_KEY=sk-...
    python src/experiments/llm_baseline.py --n 100 --model gpt-4o

Output: models/llm_baseline/results.json + comparison table
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

    # Truncate body to ~2000 chars to control costs
    body_truncated = body[:2000] if body else ""

    user_msg = f"Issue Title: {title}\n\nIssue Body:\n{body_truncated}"

    try:
        # GPT-5+ uses max_completion_tokens; older models use max_tokens
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

        # Parse JSON from response
        # Handle cases where model wraps in markdown code blocks
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


def main():
    parser = argparse.ArgumentParser(description="LLM Zero-Shot Effort Estimation Baseline")
    parser.add_argument("--n", type=int, default=100,
                        help="Number of test samples to evaluate (default: 100)")
    parser.add_argument("--model", default="gpt-4o",
                        help="OpenAI model name (default: gpt-4o)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for sampling")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY environment variable first:")
        print("  set OPENAI_API_KEY=sk-...")
        return

    # Load raw data
    data_dir = Path("data")
    parquet_path = data_dir / "raw" / "issue_pr_pairs.parquet"
    csv_path = data_dir / "raw" / "issue_pr_pairs.csv"

    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        print("No raw data found. Run the collect step first.")
        return

    # Apply same duration filter as training
    mask = (df["duration_hours"] >= 1) & (df["duration_hours"] <= 2160)
    df = df[mask].reset_index(drop=True)

    # Sample n test cases
    sample = df.sample(n=min(args.n, len(df)), random_state=args.seed)
    logger.info(f"Sampled {len(sample)} issues for LLM evaluation")
    logger.info(f"Using model: {args.model}")
    logger.info(f"Duration range: {sample['duration_hours'].min():.1f}h - {sample['duration_hours'].max():.1f}h")

    # Run predictions
    results = []
    for i, (idx, row) in enumerate(sample.iterrows()):
        title = row.get("issue_title", "") or ""
        body = row.get("issue_body", "") or ""
        actual = row["duration_hours"]
        repo = row.get("repo", "?")
        issue_num = row.get("issue_number", "?")

        logger.info(f"  [{i+1}/{len(sample)}] {repo}#{issue_num} (actual: {actual:.1f}h)")

        hours, reasoning = estimate_with_llm(title, body, model=args.model)

        if hours is not None:
            error = abs(actual - hours)
            rel_error = error / max(actual, 1e-6)
            logger.info(f"    Predicted: {hours:.1f}h, Error: {error:.1f}h ({rel_error*100:.0f}%)")
        else:
            logger.info(f"    Failed: {reasoning}")

        results.append({
            "repo": repo,
            "issue_number": issue_num,
            "issue_title": title[:100],
            "actual_hours": actual,
            "predicted_hours": hours,
            "reasoning": reasoning,
        })

        # Rate limiting — be nice to the API
        if i < len(sample) - 1:
            time.sleep(0.5)

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
    print("=" * 70)
    print(f"  MAE:      {metrics['mae']:.2f}h")
    print(f"  MdAE:     {metrics['mdae']:.2f}h")
    print(f"  Mean MRE: {metrics['mre']:.2%}")
    print(f"  PRED(25): {metrics['pred_25']:.1f}%")
    print(f"  PRED(50): {metrics['pred_50']:.1f}%")
    print(f"  R²:       {metrics['r2']:.4f}")
    print(f"  SA:       {metrics['sa']:.1f}%")
    print()

    # Compare with Model A (if available)
    model_a_results = Path("models/model_a_text_only/results.json")
    if model_a_results.exists():
        with open(model_a_results) as f:
            model_a = json.load(f).get("test_metrics", {})
        if model_a:
            print("Comparison with Model A (CodeBERT + XGBoost, full test set):")
            print(f"  {'Metric':<12} {'LLM':>10} {'Model A':>10} {'Delta':>10}")
            print(f"  {'-'*42}")
            for key, label in [("mae", "MAE"), ("mdae", "MdAE"), ("sa", "SA"),
                                ("pred_25", "PRED(25)"), ("r2", "R²")]:
                llm_val = metrics.get(key, 0)
                ma_val = model_a.get(key, 0)
                delta = llm_val - ma_val
                sign = "+" if delta > 0 else ""
                print(f"  {label:<12} {llm_val:>10.2f} {ma_val:>10.2f} {sign}{delta:>9.2f}")
            print()

    # Save
    out_dir = Path("models/llm_baseline")
    out_dir.mkdir(parents=True, exist_ok=True)

    out = {
        "model": args.model,
        "n_samples": len(valid),
        "n_failed": failed,
        "metrics": metrics,
        "predictions": results,
    }
    with open(out_dir / "results.json", "w") as f:
        json.dump(out, f, indent=2)

    results_df.to_csv(out_dir / "predictions.csv", index=False)
    logger.info(f"Results saved to {out_dir}")


if __name__ == "__main__":
    main()
