# BTOE — Beyond Text-Only Estimation

Replication and extension of the SE3M study (Fávero et al., 2022) for software effort estimation using pre-trained embedding models, enhanced with repository mining features.

## Research Questions

- **RQ1**: To what extent do text-derived features predict elapsed issue resolution time relative to a properly computed random baseline?
- **RQ2**: Does augmenting text features with repository-mined structural features yield a statistically significant improvement over text-only prediction?
- **RQ3**: Is the resulting prediction accuracy robust to encoder architecture, dimensionality reduction method, post-hoc-feature inclusion, and duration-filter threshold?

## Project Structure

```
btoe/
├── configs/
│   └── default.yaml           # All experiment parameters
├── src/
│   ├── data_collection/
│   │   ├── github_miner.py    # Mine issue-PR pairs from GitHub API
│   │   └── repo_cloner.py     # Clone repos for PyDriller analysis
│   ├── feature_extraction/
│   │   ├── nlp_features.py    # CodeBERT embeddings + derived NLP features
│   │   └── repo_features.py   # Repository-level features via PyDriller
│   ├── modeling/
│   │   └── trainer.py         # XGBoost training, evaluation, SA computation
│   ├── analysis/
│   │   ├── error_analysis.py  # Scatter plots, bucket grids
│   │   ├── example_predictions.py  # Best/worst prediction examples
│   │   ├── shap_analysis.py   # SHAP feature importance
│   │   └── data_quality.py    # Dataset quality report
│   ├── inference.py           # Live prediction (Flask web app)
│   ├── utils/
│   │   └── config.py          # Configuration management
│   └── pipeline.py            # Main orchestration pipeline (17 steps)
├── tests/
│   └── test_pipeline_correctness.py  # 32 unit + integration tests
├── app.py                     # Flask web interface
├── data/                      # Data directory (git-ignored)
├── models/                    # Trained models and results (git-ignored)
└── REPLICATION.md             # Full reproduction instructions
```

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\Activate.ps1   # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env            # Linux/Mac
# Copy-Item .env.example .env   # Windows
# Edit .env and add your GitHub Personal Access Token

# 4. Run the full study
python -m src.pipeline --step collect         # Mine issue-PR pairs
python -m src.pipeline --step clean_data      # Clean dataset
python -m src.pipeline --step nlp_features    # Extract CodeBERT embeddings
python -m src.pipeline --step repo_features   # Extract PyDriller features
python -m src.pipeline --step train           # Train Models A, B, C
python -m src.pipeline --step analyze         # Statistical comparison
python -m src.pipeline --step shap_analysis   # SHAP feature importance
python -m src.pipeline --step error_analysis  # Error analysis plots

# 5. Run ablation studies
python -m src.pipeline --step sensitivity     # Duration threshold sweep
python -m src.pipeline --step encoder_ablation          # CodeBERT vs UnixCoder vs BGE
python -m src.pipeline --step feature_selection_ablation # PCA vs PLS vs Top-K
python -m src.pipeline --step train_model_b_no_numfiles  # Model B without num_files

# 6. Run validation tests
pytest tests/test_pipeline_correctness.py -v
```

> **Note (Windows):** If you get an execution policy error when activating the venv, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` first. PyDriller requires `git` on your PATH.

## Models

| Model | Features | Purpose |
|-------|----------|---------|
| Model A | CodeBERT embeddings + 6 derived NLP features (56 total) | RQ1: text-only baseline |
| Model B | 13 PyDriller repository structural features | Structural baseline |
| Model B-restricted | Model B without num_files (post-hoc signal) | Post-hoc ablation |
| Model C | Combined text + repo features (69 total) | RQ2: signal fusion test |

## Key Results

- **SA = 34.3%** (Model A, text-only) on 90-day-cap configuration
- **SA = 34.8%** (Model C, combined) — not significantly better than A (p = 0.332)
- **Predictive ceiling at 32.0–34.8% SA** robust across encoders, feature methods, and thresholds
- Text and repo features are **substitutes, not complements**

## References

- Fávero, E.M. De Bortoli, Casanova, D., and Pimentel, A.R. (2022). SE3M: A model for software effort estimation using pre-trained embedding models. *Information and Software Technology*, 147, 106886.
- Feng, Z., Guo, D., Tang, D., et al. (2020). CodeBERT: A pre-trained model for programming and natural languages. In *Findings of EMNLP*, 1536–1547.
- Tawosi, V., Moussa, R., and Sarro, F. (2023). Agile effort estimation: Have we solved the problem yet? *IEEE Transactions on Software Engineering*, 49(4), 2677–2697.
- Shepperd, M. and MacDonell, S. (2012). Evaluating prediction systems in software project estimation. *Information and Software Technology*, 54(8), 820–827.

See `REPLICATION.md` for detailed reproduction instructions.
