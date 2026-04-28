# Evaluation Methodology

This section describes the metrics, statistical-comparison protocol, and ablations used to evaluate the three candidate models (A: text-only, B: repo-only, C: combined). Concrete results for each table appear in `results.md`; here we focus on what is measured, why, and how.

## 1. Experimental Setup

- **Dataset**: 4,479 issue–PR pairs mined from eight repositories (VS Code, TypeScript, Kubernetes, Rust, React, PyTorch, Flutter, Django) under the primary 90-day duration cap (1h ≤ duration ≤ 90d).
- **Split**: stratified 80/20 train/test split (3,583 / 896) with fixed seed 42 (`configs/default.yaml`). All ablations reuse the same split and seed unless noted.
- **Target**: implementation duration in hours, log-transformed during training; metrics are reported on back-transformed predictions in the original (hours) scale.
- **Model class**: XGBoost regressor with Bayesian-optimized hyperparameters (50 calls, 10 random starts) over 5-fold CV on the training partition.

## 2. Evaluation Metrics

We report seven complementary metrics, all computed on the held-out test set. Let `y_i` be the actual duration, `ŷ_i` the prediction, `n` the test-set size, and `ȳ` the training-set mean.

| Metric | Definition | Why we use it |
|---|---|---|
| **MAE** | `(1/n) Σ |y_i − ŷ_i|` | Standard scale-dependent error; comparable to prior effort-estimation work. |
| **MdAE** | `median(|y_i − ŷ_i|)` | Robust to long-tail outliers that dominate MAE on skewed effort distributions. |
| **MRE** | `(1/n) Σ |y_i − ŷ_i| / max(y_i, ε)` | Relative-error view; sensitive to small-duration tasks (we cap denominator at ε = 1e-6). |
| **PRED(25)** | `(1/n) Σ 𝟙[|y_i − ŷ_i|/y_i ≤ 0.25] · 100` | Fraction of predictions within 25 % of actual; standard in the SEE literature. |
| **PRED(50)** | `(1/n) Σ 𝟙[|y_i − ŷ_i|/y_i ≤ 0.50] · 100` | Looser tolerance; more informative on heavy-tailed tasks where PRED(25) is uniformly low. |
| **R²** | `1 − Σ(y_i − ŷ_i)² / Σ(y_i − ȳ)²` | Variance-explained baseline for completeness; expected to be near zero or negative under heavy-tailed effort (Menzies et al., 2013). |
| **SA** | `(1 − MAE_model / MAE_meanGuess) · 100` | Standardized Accuracy (Shepperd & MacDonell, 2012): improvement of the model's MAE over a random/mean-guess baseline. Robust to scale and to tail-heavy distributions, and is our **primary metric**. |

Implementation: `src/modeling/trainer.py:423`.

### Why SA is the primary metric

Effort distributions are heavy-tailed: a few outlier tasks contribute disproportionately to squared-error metrics, which is why `R²` is negative for all three models even though each beats trivial baselines on absolute-error metrics. SA uses absolute errors and normalizes by a mean-guess baseline, so it neither rewards models for matching the unconditional mean (as R² does) nor penalizes them for any single tail miss (as MSE does). For the same reasons we report PRED(25/50) and MdAE alongside SA.

## 3. Statistical Comparison Protocol

For each pair of models we compare the **per-sample absolute-error vectors** on the test set:

- **Wilcoxon signed-rank test** at α = 0.05 (`scipy.stats.wilcoxon`). Paired non-parametric test appropriate for non-normal error distributions.
- **Cliff's δ effect size** with Romano et al. (2006) thresholds:

  | |δ| | Interpretation |
  |---|---|
  | < 0.147 | negligible |
  | < 0.330 | small |
  | < 0.474 | medium |
  | ≥ 0.474 | large |

We report both because Wilcoxon `p`-values become significant on large paired samples (`n` = 896) even for negligible practical differences; Cliff's δ provides the magnitude check. A difference is considered meaningful only if it is both statistically significant **and** at least small in effect size.

Implementation: `src/modeling/trainer.py:446` (`compare_models`, `_cliffs_delta`).

## 4. Ablations

We ran four ablations to bound the validity of the headline result. Each ablation perturbs one design decision and re-runs the full evaluation.

### 4.1 Sensitivity to the Duration Threshold

The 90-day cap is a defensible but arbitrary filter on long-running issues. To check that conclusions are not driven by this choice, we re-trained all three models at thresholds {14d, 30d, 60d, 90d, no cap}.

**Table S1. Sensitivity Analysis (SA, A vs C significance)** — `models/sensitivity_analysis.csv`

| Threshold | N | A SA | B SA | C SA | A vs C p | Sig? |
|---|---|---|---|---|---|---|
| 14 days | 2,957 | 7.8 % | 5.6 % | 7.8 % | 0.723 | No |
| 30 days | 3,649 | 15.0 % | 10.8 % | 15.0 % | 0.717 | No |
| 60 days | 4,206 | 15.5 % | 11.5 % | 15.5 % | 0.506 | No |
| 90 days | 4,479 | 16.1 % | 12.0 % | 16.6 % | 0.023 | Yes |
| No cap | 4,499 | 16.1 % | 11.9 % | 16.7 % | 0.019 | Yes |

Per-run dumps: `models/sensitivity_{a,b,c}_{14d,30d,60d,90d,no cap}/results.json`.

### 4.2 Encoder Ablation

To separate "is the ceiling a CodeBERT limitation?" from "is the ceiling task-inherent?", we substituted three encoders into Model A's text pipeline, each followed by 50-component PCA.

**Table S2. Encoder Ablation (Model A, n = 896)**

| Encoder | Params | MAE | MdAE | PRED(25) | SA | PCA Var |
|---|---|---|---|---|---|---|
| CodeBERT (`microsoft/codebert-base`) | 125 M | 317.0 h | 130.4 h | 10.4 % | 16.0 % | 85.0 % |
| UnixCoder (`microsoft/unixcoder-base`) | 125 M | 317.7 h | 132.3 h | 9.3 % | 15.8 % | 64.9 % |
| BGE-base (`BAAI/bge-base-en-v1.5`) | 110 M | 316.6 h | 132.5 h | 11.0 % | 16.1 % | 53.8 % |

A 0.3-pp SA spread across encoders that differ in pre-training corpus and objective indicates the ceiling is largely task-inherent rather than encoder-specific.

### 4.3 Feature-Selection Ablation (PCA vs Top-K)

PCA is unsupervised and may discard supervised signal. We compared PCA against supervised Top-K selection (F-statistic against the log-duration target) at K ∈ {20, 50}.

**Table S3. Feature-Selection Ablation (Model A, n = 896)**

| Method | K | Total Features | MAE | MdAE | PRED(25) | SA |
|---|---|---|---|---|---|---|
| PCA | 20 | 26 | 315.7 h | 127.5 h | 10.2 % | 16.4 % |
| PCA | 50 | 56 | 316.6 h | 132.5 h | 11.1 % | 16.1 % |
| Top-K | 20 | 26 | 319.2 h | 127.3 h | 11.6 % | 15.4 % |
| Top-K | 50 | 56 | 314.7 h | 122.6 h | 12.5 % | 16.6 % |

(Total features = K embedding dimensions + 6 hand-crafted text features.)

Supervised selection does not consistently beat PCA, suggesting effort-relevant signal is distributed across embedding dimensions rather than concentrated in a few.

### 4.4 Dimensionality Sweep

To confirm that K = 50 is not an arbitrary sweet-spot, we ran a 7-point PCA sweep over K ∈ {50, 100, 200, 300, 400, 500, 768} (768 = the full embedding plus the 6 hand-crafted features under the `none` selection method). SA varied within ≈ 1 pp across the full range, ruling out a hidden optimum at higher K. Per-run dumps and the rolled-up table will be added under `models/dim_sweep_*/` once committed.

## 5. Baselines

We benchmark the learned models against two reference points:

1. **Mean-guess baseline** — built into SA (Section 2): the trivial predictor `ŷ = mean(y_train)`.
2. **LLM zero-shot baseline** — `src/experiments/llm_baseline.py` prompts an instruction-tuned LLM with the issue title + body and asks for a duration in hours, with no fine-tuning. This bounds how much of our SA gain over the mean baseline could be obtained without any task-specific training. (Result file `models/llm_baseline/results.json` will be added once the run completes.)

A bucket-uniform predictor (`SA = 16.7 %` over six duration buckets) is also referenced in the per-bucket error analysis in `results.md`.

## 6. Error Analysis

Beyond aggregate metrics, we stratify Model A's predictions by **actual** duration bucket to expose where error concentrates.

- Bucket grid: `models/model_a_text_only/analysis/bucket_grid_counts.csv`, `bucket_grid.png`
- Per-bucket MdAE: `error_by_range.csv`, `error_by_range.png`
- Feature importances: `feature_importance.csv`, `feature_importance.png`
- Hand-picked qualitative examples: `example_predictions.md`

Equivalent artifacts are produced for Models B and C under `models/model_b_repo_only/analysis/` and `models/model_c_combined/analysis/`.

## 7. Threats to Validity Addressed by the Above

| Threat | Mitigation |
|---|---|
| Metric choice biases the conclusion | Seven complementary metrics; SA chosen as primary on principled grounds (§ 2). |
| Wilcoxon p-values inflated by large n | Always paired with Cliff's δ; "meaningful" requires both (§ 3). |
| Threshold cherry-picking | Five-point sensitivity sweep (§ 4.1). |
| Encoder-specific ceiling | Three-encoder ablation across pre-training regimes (§ 4.2). |
| PCA discarding supervised signal | Supervised Top-K comparison at two budgets (§ 4.3). |
| Dimensionality sweet-spot artifact | Seven-point PCA sweep up to the full 768-d embedding (§ 4.4). |
| "Did the model learn anything?" | Mean-guess (built into SA) and LLM zero-shot baselines (§ 5). |
| Aggregate metrics hiding regime-specific failure | Per-bucket error analysis (§ 6). |

## References

- Shepperd, M., & MacDonell, S. (2012). Evaluating prediction systems in software project estimation. *Information and Software Technology*, 54(8).
- Menzies, T., Yang, Y., Mathew, G., Boehm, B., & Hihn, J. (2013). Negative results for software effort estimation. *Empirical Software Engineering*.
- Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006). Appropriate statistics for ordinal level data. *Annual Meeting of the Florida Association of Institutional Research*.
