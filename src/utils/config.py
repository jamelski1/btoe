"""Configuration loading and management."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.yaml"


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    with open(path) as f:
        return yaml.safe_load(f)


def get_github_token() -> str:
    """Get GitHub token from environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not set. Copy .env.example to .env and add your token."
        )
    return token


def get_data_dir() -> Path:
    """Get data directory path."""
    data_dir = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_model_dir() -> Path:
    """Get model directory path."""
    model_dir = Path(os.getenv("MODEL_DIR", PROJECT_ROOT / "models"))
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir
