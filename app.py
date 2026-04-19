"""Flask web app — Issue Duration Estimator.

Usage:
    python app.py                         # default port 5000
    python app.py --port 8080
    python app.py --config configs/mansi.yaml
"""

import argparse
import logging

from flask import Flask, jsonify, render_template, request

from src.inference import ModelPredictor
from src.utils.config import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
predictor: ModelPredictor | None = None

# Text-based task categories where Model A (CodeBERT + NLP) performs best,
# shown in the UI as a dropdown to help users frame their estimate.
TEXT_TASK_CATEGORIES = [
    {"id": "bug_fix",      "label": "Bug fix",            "typical_hours": "2–8h"},
    {"id": "documentation", "label": "Documentation",      "typical_hours": "1–4h"},
    {"id": "refactor",     "label": "Refactor / cleanup", "typical_hours": "4–16h"},
    {"id": "small_feature", "label": "Small feature",      "typical_hours": "8–24h"},
    {"id": "test_addition", "label": "Test addition",      "typical_hours": "2–6h"},
    {"id": "config_change", "label": "Config change",      "typical_hours": "1–3h"},
]


def get_predictor() -> ModelPredictor:
    global predictor
    if predictor is None:
        predictor = ModelPredictor(app.config["SE3M_CONFIG"])
    return predictor


def effort_tier(hours: float | None) -> str | None:
    """Coarse effort bucket for a predicted duration."""
    if hours is None:
        return None
    if hours < 1:
        return "Trivial"
    if hours < 4:
        return "Small"
    if hours < 16:
        return "Medium"
    if hours < 40:
        return "Large"
    return "XL"


# ------------------------------------------------------------------ #
# Routes                                                               #
# ------------------------------------------------------------------ #

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/status")
def status():
    p = get_predictor()
    return jsonify({
        "model_a": p.is_available("a"),
        "model_b": p.is_available("b"),
        "model_c": p.is_available("c"),
    })


@app.get("/categories")
def categories():
    """Text-based task categories Model A handles well."""
    return jsonify({"categories": TEXT_TASK_CATEGORIES})


@app.post("/predict")
def predict():
    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()
    files_raw = (data.get("files") or "").strip()
    files = [f.strip() for f in files_raw.split(",") if f.strip()] if files_raw else []
    repo_url = (data.get("repo_url") or "").strip()
    category = (data.get("category") or "").strip()

    p = get_predictor()
    results = {"category": category or None}

    hours_a, err_a = p.predict_text_only(title, body)
    results["model_a"] = {
        "hours": hours_a,
        "error": err_a,
        "metrics": p.get_metrics("a"),
        "effort_tier": effort_tier(hours_a),
    }

    hours_b, err_b = p.predict_repo_only(files, repo_url=repo_url)
    results["model_b"] = {
        "hours": hours_b,
        "error": err_b,
        "metrics": p.get_metrics("b"),
        "has_repo": bool(repo_url),
        "effort_tier": effort_tier(hours_b),
    }

    hours_c, err_c = p.predict_combined(title, body, files=files, repo_url=repo_url)
    results["model_c"] = {
        "hours": hours_c,
        "error": err_c,
        "metrics": p.get_metrics("c"),
        "has_repo": bool(repo_url),
        "effort_tier": effort_tier(hours_c),
    }

    return jsonify(results)


# ------------------------------------------------------------------ #
# Entry point                                                          #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--config", default=None, help="Path to config YAML")
    args = parser.parse_args()

    cfg = load_config(args.config)
    app.config["SE3M_CONFIG"] = cfg

    logger.info("Starting Issue Duration Estimator on http://localhost:%d", args.port)
    app.run(host="0.0.0.0", port=args.port, debug=False)
