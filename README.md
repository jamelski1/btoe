# BTOE — Beyond Text-Only Estimation

Replication and extension of the SE3M study (Ribeiro et al., 2022) for software effort estimation using pre-trained embedding models, enhanced with repository mining features.

## Research Questions

- **RQ1**: How accurately can CodeBERT-based text embeddings predict feature implementation duration? (replicating SE3M)
- **RQ2**: Does combining NLP features with repository-mined structural features improve prediction accuracy?

## Project Structure

```
btoe/
├── configs/            # Configuration files
│   └── default.yaml    # Default experiment configuration
├── src/
│   ├── data_collection/
│   │   ├── github_miner.py   # Mine issue-PR pairs from GitHub
│   │   └── repo_cloner.py    # Clone repos for PyDriller analysis
│   ├── feature_extraction/
│   │   ├── nlp_features.py   # CodeBERT embeddings + derived NLP features
│   │   └── repo_features.py  # Repository-level features via PyDriller
│   ├── modeling/
│   │   └── trainer.py         # XGBoost training with Bayesian optimization
│   ├── analysis/
│   │   └── shap_analysis.py   # SHAP feature importance + error analysis
│   ├── utils/
│   │   └── config.py          # Configuration management
│   └── pipeline.py            # Main orchestration pipeline
├── data/               # Data directory (git-ignored)
├── models/             # Trained models and results (git-ignored)
├── notebooks/          # Jupyter notebooks for exploration
└── tests/              # Unit tests
```

## Setup

```powershell
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
Copy-Item .env.example .env
# Edit .env and add your GitHub token (e.g. notepad .env)

# 4. Run pipeline steps
python -m src.pipeline --step validate   # Validate target repos
python -m src.pipeline --step collect    # Mine issue-PR pairs
python -m src.pipeline --step features   # Extract NLP + repo features
python -m src.pipeline --step train      # Train Models A, B, C
python -m src.pipeline --step analyze    # SHAP + error analysis
python -m src.pipeline --step all        # Run everything
```

> **Note (Windows):** If you get an execution policy error when activating the venv, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` first. PyDriller requires `git` on your PATH — install [Git for Windows](https://git-scm.com/download/win) if needed.

## Models

| Model | Features | Purpose |
|-------|----------|---------|
| Model A | CodeBERT embeddings + NLP derived | RQ1 baseline (SE3M replication) |
| Model B | Repository-mined features only | Structural baseline |
| Model C | Combined NLP + repo features | RQ2 test (signal fusion) |

## References

- Ribeiro, R., et al. (2022). SE3M: A model for software effort estimation using pre-trained embedding models. *Information and Software Technology*, 147, 106899.
- Feng, Z., et al. (2020). CodeBERT: A pre-trained model for programming and natural languages. *EMNLP 2020*.
