# Results

## 4.1 Dataset

We mined 4,499 issue-PR pairs from eight actively maintained open-source repositories spanning four distinct organizational sponsors: VS Code and TypeScript (Microsoft), Kubernetes (CNCF), Rust (Rust Foundation), React and PyTorch (Meta), Flutter (Google), and Django (Django Software Foundation). After applying the duration filter (1 hour to 90 days), the final dataset comprised 4,479 pairs. The duration distribution was heavily right-skewed (mean = 374h, median = 146h, std = 492h), motivating the use of a log-transform on the target variable during training. The dataset was split 80/20 into a training set (3,583 samples) and a held-out test set (896 samples), with a fixed random seed (42) for reproducibility.

## 4.2 RQ1: Text-Only Prediction Accuracy

Model A (text-only) achieved a Standardized Accuracy (SA) of 16.0% on the held-out test set, confirming that CodeBERT embeddings provide modest but positive predictive value for feature implementation duration (Table 1). The model correctly placed predictions in the right duration bucket 22.8% of the time (compared to a 6-bucket uniform baseline of 16.7%), with its strongest performance in the 3–7 day range (53.4% bucket accuracy, median absolute error of 48h).

**Table 1. Primary Model Comparison (Test Set, n = 896)**

| Metric      | Model A (Text) | Model B (Repo) | Model C (Combined) |
|-------------|---------------|----------------|---------------------|
| MAE         | 317.0h        | 332.3h         | 315.7h              |
| MdAE        | 130.4h        | 121.9h         | 129.0h              |
| Mean MRE    | 498.7%        | 593.7%         | 480.1%              |
| PRED(25)    | 10.4%         | 9.8%           | 10.6%               |
| PRED(50)    | 22.4%         | 19.9%          | 22.4%               |
| SA          | 16.0%         | 12.0%          | 16.4%               |
| R²          | −0.146        | −0.259         | −0.150              |

Negative R² values across all models indicate that the conditional mean learned by each model performs worse on MSE than the unconditional training-set mean. This is a known pattern for heavy-tailed effort distributions: the unconditional mean absorbs tail variance that the model cannot capture, while models that attempt to differentiate between tasks incur large squared errors on the long tail (Menzies et al., 2013). SA, which uses absolute rather than squared errors, treats these tail failures more leniently and provides a more robust evaluation for skewed effort data (Shepperd & MacDonell, 2012). We therefore use SA as the primary metric throughout this analysis while reporting R² for completeness.

Feature importance analysis revealed that `word_count` was the single most predictive feature in Model A (importance = 0.066), followed by PCA embedding components. This indicates that issue description length—a rough proxy for task complexity—provides the strongest individual signal, while the semantic embedding captures more nuanced patterns across its distributed representation.

## 4.3 RQ2: Does Combining Features Help?

Model C (combined) achieved marginally higher SA (16.4%) and lower MAE (315.7h) than Model A (SA = 16.0%, MAE = 317.0h). However, a Wilcoxon signed-rank test found this difference was not statistically significant (W = 191,518, p = 0.225), and the Cliff's delta effect size was negligible (δ = 0.013).

Model A significantly outperformed Model B (W = 166,293, p < 0.001), though the practical effect was negligible (Cliff's δ = −0.029). Notably, Model B exhibited degenerate behavior, predicting durations within the "3–7 days" bucket for 97% of test samples regardless of actual duration (bucket accuracy = 14.7%). This collapse to a near-constant predictor indicates that repository structural features alone—churn, coupling, file age—lack sufficient discriminative signal for effort estimation without semantic context.

In Model C, the feature importance shifted: repository features (`avg_change_frequency`, `avg_churn_per_file`, `avg_file_age_days`) occupied three of the top five positions, with text features (`word_count`, `text_length`) also ranking highly. The combined model successfully integrated both signal sources, but the additional information did not translate into a statistically significant or practically meaningful accuracy improvement.

**Table 2. Pairwise Statistical Comparison (90-Day Threshold)**

| Comparison   | Wilcoxon W  | p-value  | Significant (α=0.05)? | Cliff's δ | Effect Size |
|--------------|-------------|----------|------------------------|-----------|-------------|
| A vs B       | 166,293     | < 0.001  | Yes                    | −0.029    | Negligible  |
| A vs C       | 191,518     | 0.225    | No                     | +0.013    | Negligible  |
| B vs C       | 162,706     | < 0.001  | Yes                    | +0.040    | Negligible  |

## 4.4 Sensitivity Analysis

To assess robustness to the choice of duration threshold—an inherently arbitrary filtering decision—we retrained all three models at five thresholds: 14, 30, 60, and 90 days, plus no cap (Table 3). At each threshold we report the Wilcoxon p-value for the A vs. C comparison.

**Table 3. Sensitivity Analysis Across Duration Thresholds**

| Threshold | N     | A SA   | B SA  | C SA   | A vs C p | Sig? |
|-----------|-------|--------|-------|--------|----------|------|
| 14 days   | 2,957 | 7.8%   | 5.6%  | 7.8%   | 0.723    | No   |
| 30 days   | 3,649 | 15.0%  | 10.8% | 15.0%  | 0.717    | No   |
| 60 days   | 4,206 | 15.5%  | 11.5% | 15.5%  | 0.506    | No   |
| 90 days   | 4,479 | 16.1%  | 12.0% | 16.6%  | 0.023    | Yes  |
| No cap    | 4,499 | 16.1%  | 11.9% | 16.7%  | 0.019    | Yes  |

*Note: A SA and C SA are identical at displayed precision for the 14-day and 30-day thresholds; values differ at the third decimal place (e.g., 7.765% vs. 7.805% at 14 days).*

At the 90-day and uncapped thresholds, the A vs. C comparison becomes statistically detectable (p < 0.05), but the Cliff's delta effect size remains negligible across all thresholds (δ < 0.04). We interpret this as evidence that any marginal contribution of repository features is concentrated in the long-tail regime where large paired-sample sizes (n > 4,400) provide sufficient power to detect very small differences. However, this statistical detectability does not translate into practically meaningful predictive gain: the SA improvement from Model A to Model C at 90 days is 0.5 percentage points (16.1% → 16.6%), within the range of run-to-run variation observed in the encoder and feature selection ablations.

## 4.5 Encoder Ablation

To determine whether the performance ceiling reflects a limitation of the CodeBERT encoder or a task-inherent ceiling, we repeated the Model A evaluation with three encoders: CodeBERT (125M parameters, code-specialized), UnixCoder (125M, CodeBERT successor with data-flow awareness), and BGE-base-en-v1.5 (110M, general-purpose semantic embedding model).

**Table 4. Encoder Ablation (Model A, Test Set)**

| Encoder       | Params | MAE    | MdAE   | PRED(25) | SA    | PCA Var |
|---------------|--------|--------|--------|----------|-------|---------|
| CodeBERT      | 125M   | 317.0h | 130.4h | 10.4%    | 16.0% | 85.0%   |
| UnixCoder     | 125M   | 317.7h | 132.3h | 9.3%     | 15.8% | 64.9%   |
| BGE-base      | 110M   | 316.6h | 132.5h | 11.0%    | 16.1% | 53.8%   |

All three encoders produced closely matched downstream performance (SA range: 15.8–16.1%), within a 0.3 percentage-point band, despite capturing between 54–85% of total embedding variance in 50 PCA components. The fact that BGE—a general-purpose semantic model with no code-specific pre-training—matched the code-specialized encoders suggests that the effort-relevant signal in issue text is carried by general linguistic features (e.g., description length, vocabulary complexity) rather than code-specific semantics.

## 4.6 Feature Selection Ablation

We further compared unsupervised (PCA) and supervised (Top-K by F-statistic) dimensionality reduction at feature budgets of 20 and 50.

**Table 5. Feature Selection Ablation (Model A, Test Set)**

| Method  | K  | Features | MAE    | MdAE   | PRED(25) | SA    |
|---------|----|----------|--------|--------|----------|-------|
| PCA     | 20 | 26       | 315.7h | 127.5h | 10.2%    | 16.4% |
| PCA     | 50 | 56       | 316.6h | 132.5h | 11.1%    | 16.1% |
| Top-K   | 20 | 26       | 319.2h | 127.3h | 11.6%    | 15.4% |
| Top-K   | 50 | 56       | 314.7h | 122.6h | 12.5%    | 16.6% |

All four configurations produced SA within a 1.2 percentage-point range (15.4–16.6%), confirming that the performance ceiling is robust to both the feature selection method and the feature budget. Supervised selection did not consistently outperform unsupervised PCA: at K=20, PCA achieved higher SA (16.4% vs. 15.4%), while at K=50, Top-K held a marginal advantage (16.6% vs. 16.1%). This pattern suggests the effort-relevant signal in the embedding space is distributed across many dimensions rather than concentrated in a few identifiable ones.

## 4.7 Error Analysis

A bucketed analysis of Model A's test predictions revealed systematic patterns in prediction accuracy across duration ranges (Table 6).

**Table 6. Model A Prediction Error by Actual Duration Bucket**

| Actual Duration | N   | MdAE  | Bucket Accuracy |
|-----------------|-----|-------|-----------------|
| < 1 day         | 86  | 69h   | 0%              |
| 1 day           | 90  | 82h   | 1%              |
| 1–3 days        | 157 | 73h   | 24%             |
| 3–7 days        | 133 | 48h   | 53%             |
| 1–4 weeks       | 263 | 221h  | 36%             |
| > 4 weeks       | 167 | 1,002h| 1%              |

The model achieved its best performance in the 3–7 day range (median error = 48h, bucket accuracy = 53%), corresponding to the center of the training distribution. Performance degraded sharply at the extremes: sub-day tasks were systematically over-predicted (median error of 69–82h for tasks actually taking <24h), while tasks exceeding four weeks were massively under-predicted (median error of 1,002h). This regression-to-the-mean pattern indicates that current feature representations lack sufficient discriminative power to distinguish extreme-duration issues from typical ones.

Qualitative examination of individual predictions illustrated these patterns. In the model's strongest bucket (3–7 days), predictions could be remarkably precise: a Kubernetes image build failure (#136350, actual 4.7 days) was predicted at 4.7 days (2% error), and a VS Code MSAL authentication issue (#240307, actual 5.8 days) was predicted at 6.0 days (4% error). However, the model's reliance on textual volume led to systematic failures on short-duration tasks with brief descriptions: a VS Code UI fix (#243115, actual 1.7 hours) was predicted at 8.2 days (11,628% error), where the issue body consisted primarily of a screenshot with minimal text. This dependence on description length rather than semantic content—consistent with `word_count` being the top feature—represents a fundamental limitation of the current approach.
