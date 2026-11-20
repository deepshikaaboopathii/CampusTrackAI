import pytest
import os
import json
from ml.preprocessing import build_preprocessor, NUMERIC_FEATURES, CATEGORICAL_FEATURES
from ml.predict import analyze_student_profile, get_loaded_model
from ml.train_model import METRICS_PATH, MODEL_SAVE_PATH

def test_model_files_exist():
    assert os.path.exists(MODEL_SAVE_PATH), "Model artifact .joblib must exist"
    assert os.path.exists(METRICS_PATH), "Model metrics .json must exist"

def test_metrics_json_structure():
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "best_model" in data
    assert "models" in data
    assert len(data["models"]) == 3
    for name in ["Logistic Regression", "Random Forest", "Gradient Boosting"]:
        assert name in data["models"]
        m = data["models"][name]
        assert "accuracy" in m
        assert "precision" in m
        assert "recall" in m
        assert "f1_score" in m
        assert "roc_auc" in m
        assert "cv_f1_mean" in m
        assert "confusion_matrix" in m

def test_inference_ready_candidate():
    high_candidate = {
        "department": "Computer Science",
        "cgpa": 9.2,
        "attendance": 95.0,
        "backlog_count": 0,
        "aptitude_score": 90.0,
        "technical_score": 95.0,
        "communication_score": 88.0,
        "programming_rating": 4.8,
        "projects_count": 4,
        "certifications_count": 3,
        "internships_count": 2,
        "soft_skills_score": 90.0
    }
    result = analyze_student_profile(high_candidate)
    assert result["placement_probability"] >= 70.0
    assert result["readiness_category"] in ["Placement Ready", "Developing"]
    assert len(result["strengths"]) >= 3
    assert len(result["roadmap_30_days"]) == 3

def test_inference_at_risk_candidate():
    at_risk = {
        "department": "Mechanical",
        "cgpa": 5.8,
        "attendance": 65.0,
        "backlog_count": 3,
        "aptitude_score": 45.0,
        "technical_score": 40.0,
        "communication_score": 50.0,
        "programming_rating": 1.5,
        "projects_count": 0,
        "certifications_count": 0,
        "internships_count": 0,
        "soft_skills_score": 50.0
    }
    result = analyze_student_profile(at_risk)
    assert result["placement_probability"] < 50.0
    assert result["readiness_category"] == "Needs Improvement"
    assert len(result["skill_gaps"]) >= 3
    assert len(result["recommended_courses"]) >= 2
    assert "disclaimer" in result

