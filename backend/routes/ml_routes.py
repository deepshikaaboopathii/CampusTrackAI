import os
import json
from flask import Blueprint, request, jsonify
from ml.predict import analyze_student_profile
from ml.train_model import train_and_evaluate_all, METRICS_PATH
from backend.services.auth_service import token_required

ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")

@ml_bp.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() or {}
    try:
        analysis = analyze_student_profile(data)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@ml_bp.route("/metrics", methods=["GET"])
def get_metrics():
    if not os.path.exists(METRICS_PATH):
        # Auto-train if not yet trained
        try:
            train_and_evaluate_all()
        except Exception as e:
            return jsonify({"error": f"Model not trained yet and auto-training failed: {str(e)}"}), 500

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": f"Failed to read model metrics: {str(e)}"}), 500

@ml_bp.route("/retrain", methods=["POST"])
@token_required
def retrain_model():
    try:
        new_metrics = train_and_evaluate_all()
        # Invalidate loaded model in memory
        from ml import predict as pred_mod
        pred_mod._model = None
        return jsonify({
            "message": "Model retrained and evaluated successfully against current database records.",
            "metrics": new_metrics
        }), 200
    except Exception as e:
        return jsonify({"error": f"Retraining failed: {str(e)}"}), 500

