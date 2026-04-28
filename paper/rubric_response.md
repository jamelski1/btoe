# Rubric Response — BTOE Study

## 1. Testing Technique (20 %)

We use a **held-out test-set protocol** with statistical comparison across three competing model configurations.

**Data partitioning.** 4,479 issue–PR pairs (8 repositories, 90-day duration cap) are split 80 / 20 into train (3,583) and test (896) sets, stratified and seeded with `random_state = 42` for reproducibility.

**Model training.** XGBoost regressors are trained on log-transformed duration. Hyperparameters are tuned via **Bayesian optimization** (50 calls, 10 random starts) over **5-fold cross-validation on the training partition only** — the test set is never seen during model selection.

**Three model configurations** are trained under identical pipelines, isolating the contribution of each feature family:

| Model | Features | Question it answers |
|---|---|---|
| A — Text-only | CodeBERT embedding (768-d → PCA-50) + 6 hand-crafted text features | RQ1: SE3M baseline replication |
| B — Repo-only | PyDriller-mined repo metrics (churn, coupling, file age, change frequency) | Structural ablation |
| C — Combined | A's features ∪ B's features | RQ2: does fusion help? |

**Statistical comparison.** For each pair (A vs B, A vs C, B vs C) we compute per-sample absolute errors on the test set and apply:

- **Wilcoxon signed-rank test** (paired, non-parametric, α = 0.05) — does the difference exceed noise?
- **Cliff's δ** with Romano et al. (2006) thresholds (negligible < 0.147 < small < 0.330 < medium < 0.474 < large) — is the difference practically meaningful?

A finding is reported as meaningful only when both criteria are met. This guards against the well-known failure mode where large `n` makes Wilcoxon flag trivial differences as significant.

**Implementation:** `src/modeling/trainer.py:423` (`compute_metrics`), `:446` (`compare_models`), `:481` (`_cliffs_delta`).

## 2. Evaluation Metrics (20 %)

We report **seven complementary metrics** computed on the held-out test set, each chosen for a specific reason given heavy-tailed effort distributions (mean 374 h, median 146 h, std 492 h).

| Metric | Formula | Role |
|---|---|---|
| MAE | `(1/n) Σ |y − ŷ|` | Scale-dependent baseline; comparable to SE3M and other prior work. |
| MdAE | `median(|y − ŷ|)` | Robust to long-tail outliers that dominate MAE. |
| MRE | `(1/n) Σ |y − ŷ| / max(y, ε)` | Relative-error view; sensitive to small-duration tasks. |
| PRED(25) | % of predictions with relative error ≤ 25 % | Standard SEE threshold metric. |
| PRED(50) | % of predictions with relative error ≤ 50 % | Looser tolerance, more informative under heavy tails. |
| R² | `1 − Σ(y − ŷ)² / Σ(y − ȳ)²` | Variance explained; expected to be ≤ 0 for heavy-tailed effort (Menzies 2013). |
| **SA** | `(1 − MAE_model / MAE_meanGuess) · 100` | **Primary metric.** Standardized Accuracy (Shepperd & MacDonell 2012): improvement over a mean-guess baseline. Robust to scale and tails. |

**Why SA is primary.** R² is negative for all three models because the unconditional mean absorbs tail variance that no model can capture; SA uses absolute errors and a built-in random baseline, so it penalizes neither tail miss nor mean-matching, and is the metric of record in the SE-effort-estimation literature. We additionally report MdAE and PRED(25/50) so the reader can see absolute, relative, and threshold-based views.

**Headline numbers (90-day cap, n = 896):**

| Metric | Model A (Text) | Model B (Repo) | Model C (Combined) |
|---|---|---|---|
| MAE | 317.0 h | 332.3 h | 315.7 h |
| MdAE | 130.4 h | 121.9 h | 129.0 h |
| MRE | 4.99 | 5.94 | 4.80 |
| PRED(25) | 10.4 % | 9.8 % | 10.6 % |
| PRED(50) | 22.4 % | 19.9 % | 22.4 % |
| **SA** | **16.0 %** | **12.0 %** | **16.4 %** |
| R² | −0.146 | −0.259 | −0.150 |

**Pairwise statistical comparison:**

| Comparison | Wilcoxon p | Cliff's δ | Verdict |
|---|---|---|---|
| A vs B | 7.8 × 10⁻⁶ | −0.029 (negligible) | Significant but practically negligible. |
| A vs C | 0.225 | +0.013 (negligible) | Not significant; effect negligible. |
| B vs C | 8.1 × 10⁻⁷ | +0.040 (negligible) | Significant but practically negligible. |

**Per-bucket error analysis** (`models/model_a_text_only/analysis/`) stratifies metrics by actual-duration bucket, exposing where error concentrates: best in 3–7 day range (MdAE = 48 h, bucket accuracy 53 %), worst on tasks > 4 weeks (MdAE = 1,002 h).

## 3. Research Questions (20 %)

Two RQs framed as a replication-plus-extension of SE3M (Ribeiro et al., 2022):

**RQ1 — Replication: How accurately can pre-trained text embeddings predict feature implementation duration?**

- *Hypothesis*: CodeBERT embeddings of issue text alone provide modest but positive predictive signal for effort, replicating SE3M's central finding on a different dataset.
- *Test*: Model A's metrics on the held-out test set, compared to a mean-guess baseline via SA.
- *Finding*: SA = 16.0 %, PRED(25) = 10.4 %; the model beats mean-guess by ≈ 16 % on absolute error, with strongest performance in the 3–7 day bucket. RQ1 is supported with a clear ceiling.

**RQ2 — Extension: Does combining NLP features with repository-mined structural features improve prediction accuracy?**

- *Hypothesis*: Repository signals (churn, coupling, file age, change frequency) carry effort-relevant information orthogonal to issue text, so Model C should outperform Model A.
- *Test*: A vs C comparison via Wilcoxon + Cliff's δ on per-sample absolute errors at the held-out test set.
- *Finding*: SA improves marginally (16.0 % → 16.4 %), but Wilcoxon p = 0.225 and Cliff's δ = +0.013 (negligible). RQ2 is **not supported**: combining features yields no statistically significant or practically meaningful gain. A secondary finding — Model B alone collapses toward a constant predictor (97 % of test samples in the "3–7 days" bucket) — shows that repo features lack discriminative signal in isolation.

This null result is itself the contribution: it bounds the marginal value of repo-mining-only features when added to a competitive text baseline.

## 4. Evaluation Plan (20 %)

Beyond the headline three-model comparison, we ran **four ablations** and **two baselines** to bound the validity of the conclusions.

### 4.1 Ablations

| # | Ablation | What varies | Why | Result file |
|---|---|---|---|---|
| 1 | **Duration-threshold sensitivity** | Cap at {14d, 30d, 60d, 90d, no cap} | The 90-day cap is defensible but arbitrary; verify conclusions are not threshold-driven | `models/sensitivity_analysis.csv`; per-run dumps in `models/sensitivity_{a,b,c}_*/` |
| 2 | **Encoder ablation** | CodeBERT vs UnixCoder vs BGE-base-en-v1.5 | Separate "is this a CodeBERT ceiling?" from "is this a task-inherent ceiling?" | `paper/results.md` § 4.5 |
| 3 | **Feature-selection ablation** | PCA vs supervised Top-K (F-statistic), at K ∈ {20, 50} | PCA is unsupervised and may discard supervised signal | `paper/results.md` § 4.6 |
| 4 | **Dimensionality sweep** | PCA K ∈ {50, 100, 200, 300, 400, 500, 768} | Confirm K = 50 is not a hidden sweet-spot | sweep step `dimensionality_sweep` in pipeline |

**Sensitivity (Table S1).**

| Threshold | N | A SA | B SA | C SA | A vs C p | Sig? |
|---|---|---|---|---|---|---|
| 14 days | 2,957 | 7.8 % | 5.6 % | 7.8 % | 0.723 | No |
| 30 days | 3,649 | 15.0 % | 10.8 % | 15.0 % | 0.717 | No |
| 60 days | 4,206 | 15.5 % | 11.5 % | 15.5 % | 0.506 | No |
| 90 days | 4,479 | 16.1 % | 12.0 % | 16.6 % | 0.023 | Yes |
| No cap | 4,499 | 16.1 % | 11.9 % | 16.7 % | 0.019 | Yes |

A vs C reaches significance only at ≥ 90 d, and Cliff's δ stays negligible everywhere — so the marginal A→C gain is concentrated in the long tail and remains practically negligible.

**Encoder (Table S2).**

| Encoder | Params | MAE | MdAE | PRED(25) | SA | PCA Var |
|---|---|---|---|---|---|---|
| CodeBERT | 125 M | 317.0 h | 130.4 h | 10.4 % | 16.0 % | 85.0 % |
| UnixCoder | 125 M | 317.7 h | 132.3 h | 9.3 % | 15.8 % | 64.9 % |
| BGE-base | 110 M | 316.6 h | 132.5 h | 11.0 % | 16.1 % | 53.8 % |

A 0.3 pp SA spread across pre-training regimes — including a general-purpose semantic encoder (BGE) — indicates the ceiling is task-inherent, not encoder-specific.

**Feature selection (Table S3).**

| Method | K | MAE | MdAE | PRED(25) | SA |
|---|---|---|---|---|---|
| PCA | 20 | 315.7 h | 127.5 h | 10.2 % | 16.4 % |
| PCA | 50 | 316.6 h | 132.5 h | 11.1 % | 16.1 % |
| Top-K | 20 | 319.2 h | 127.3 h | 11.6 % | 15.4 % |
| Top-K | 50 | 314.7 h | 122.6 h | 12.5 % | 16.6 % |

Supervised selection does not consistently beat PCA; signal is distributed across embedding dimensions.

**Dimensionality sweep.** SA varies within ≈ 1 pp across K ∈ {50, 100, 200, 300, 400, 500, 768}, ruling out a hidden optimum at higher K.

### 4.2 Baselines

- **Mean-guess** — built into SA (`ŷ = mean(y_train)`); SA quantifies improvement over this trivial predictor.
- **Bucket-uniform** — 16.7 % across six duration buckets; Model A reaches 22.8 %.
- **LLM zero-shot** (`src/experiments/llm_baseline.py`) — instruction-tuned LLM prompted with issue title + body, no fine-tuning. Bounds how much SA gain over mean-guess could be obtained without task-specific training.

### 4.3 Threats-to-Validity Mitigation Map

| Threat | Mitigation |
|---|---|
| Metric choice biases the conclusion | Seven complementary metrics; SA primary on principled grounds. |
| Wilcoxon `p`-values inflated by large `n` | Always paired with Cliff's δ; both required. |
| Threshold cherry-picking | Five-point sensitivity sweep. |
| Encoder-specific ceiling | Three-encoder ablation across pre-training regimes. |
| PCA discarding supervised signal | Top-K supervised selection at two budgets. |
| Dimensionality sweet-spot artifact | Seven-point PCA sweep up to full 768-d embedding. |
| "Did the model learn anything?" | Mean-guess (built into SA), bucket-uniform, LLM zero-shot. |
| Aggregate metrics hiding regime-specific failure | Per-bucket error analysis with qualitative examples. |

### 4.4 Reproducibility

Fixed random seed (42), versioned `configs/default.yaml`, deterministic 80/20 split, all model artifacts and per-sample predictions persisted under `models/`, end-to-end re-runnable via `python -m src.pipeline --step all`.

## 5. Feedback from Other Team

*[To be inserted from the separate feedback document — this section will summarize the reviewing team's comments and our responses / changes incorporated.]*

## References

- Shepperd, M., & MacDonell, S. (2012). Evaluating prediction systems in software project estimation. *Information and Software Technology*, 54(8).
- Menzies, T., Yang, Y., Mathew, G., Boehm, B., & Hihn, J. (2013). Negative results for software effort estimation. *Empirical Software Engineering*.
- Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006). Appropriate statistics for ordinal level data. *Annual Meeting of the Florida Association of Institutional Research*.
- Ribeiro, R., et al. (2022). SE3M: A model for software effort estimation using pre-trained embedding models. *Information and Software Technology*, 147, 106899.
- Feng, Z., et al. (2020). CodeBERT: A pre-trained model for programming and natural languages. *EMNLP 2020*.
