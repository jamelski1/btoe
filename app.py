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


def get_predictor() -> ModelPredictor:
    global predictor
    if predictor is None:
        predictor = ModelPredictor(app.config["SE3M_CONFIG"])
    return predictor


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


@app.post("/predict")
def predict():
    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()
    files_raw = (data.get("files") or "").strip()
    files = [f.strip() for f in files_raw.split(",") if f.strip()] if files_raw else []

    p = get_predictor()
    results = {}

    hours_a, err_a = p.predict_text_only(title, body)
    results["model_a"] = {
        "hours": hours_a,
        "error": err_a,
        "metrics": p.get_metrics("a"),
    }

    hours_b, err_b = p.predict_repo_only(files)
    results["model_b"] = {
        "hours": hours_b,
        "error": err_b,
        "metrics": p.get_metrics("b"),
    }

    hours_c, err_c = p.predict_combined(title, body, files=files)
    results["model_c"] = {
        "hours": hours_c,
        "error": err_c,
        "metrics": p.get_metrics("c"),
    }

    return jsonify(results)


# ------------------------------------------------------------------ #
# Entry point                                                          #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--config", default=None, help="Path to config YAML")
    parser.add_argument("--ngrok", action="store_true", help="Expose via ngrok tunnel")
    args = parser.parse_args()

    cfg = load_config(args.config)
    app.config["SE3M_CONFIG"] = cfg

    if args.ngrok:
        try:
            from pyngrok import ngrok
            tunnel = ngrok.connect(args.port)
            logger.info("ngrok tunnel: %s", tunnel.public_url)
        except ImportError:
            logger.warning("pyngrok not installed — run: pip install pyngrok")

    logger.info("Starting Issue Duration Estimator on http://localhost:%d", args.port)
    app.run(host="0.0.0.0", port=args.port, debug=False)
