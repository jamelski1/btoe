"""Flask web app — Issue Duration Estimator.

Usage:
    python app.py                         # default port 5000
    python app.py --port 8080
    python app.py --config configs/mansi.yaml
"""

# macOS: must be set before numpy / torch / transformers are imported.
# numpy (via MKL) and torch both load OpenMP runtimes; without these flags
# the duplicate load segfaults at import time on macOS.
import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

print("[startup] env vars set", flush=True)

# macOS: torch and xgboost each bundle their own libomp.dylib. Loading
# xgboost AFTER torch crashes on macOS (arm64 especially). Importing
# xgboost first makes its libomp "win" and torch reuses it.
print("[startup] importing xgboost (pre-torch, macOS libomp workaround)", flush=True)
import xgboost  # noqa: F401

import argparse
import logging

print("[startup] importing flask", flush=True)
from flask import Flask, jsonify, render_template, request

print("[startup] importing ModelPredictor", flush=True)
from src.inference import ModelPredictor

print("[startup] importing load_config", flush=True)
from src.utils.config import load_config

print("[startup] imports complete", flush=True)

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
    repo_url = (data.get("repo_url") or "").strip()

    p = get_predictor()
    results = {}

    hours_a, err_a = p.predict_text_only(title, body)
    results["model_a"] = {
        "hours": hours_a,
        "error": err_a,
        "metrics": p.get_metrics("a"),
    }

    hours_b, err_b = p.predict_repo_only(files, repo_url=repo_url)
    results["model_b"] = {
        "hours": hours_b,
        "error": err_b,
        "metrics": p.get_metrics("b"),
        "has_repo": bool(repo_url),
    }

    hours_c, err_c = p.predict_combined(title, body, files=files, repo_url=repo_url)
    results["model_c"] = {
        "hours": hours_c,
        "error": err_c,
        "metrics": p.get_metrics("c"),
        "has_repo": bool(repo_url),
    }

    return jsonify(results)


# ------------------------------------------------------------------ #
# Entry point                                                          #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("[startup] parsing args", flush=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--config", default=None, help="Path to config YAML")
    args = parser.parse_args()

    print(f"[startup] loading config from {args.config}", flush=True)
    cfg = load_config(args.config)
    app.config["SE3M_CONFIG"] = cfg

    print(f"[startup] calling app.run on port {args.port}", flush=True)
    logger.info("Starting Issue Duration Estimator on http://localhost:%d", args.port)
    app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)
