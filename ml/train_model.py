"""
CampusTrack AI - Model Training & Evaluation Engine
Trains Logistic Regression, Random Forest, and Gradient Boosting Classifiers,
compares metrics (Accuracy, Precision, Recall, F1, ROC-AUC, 5-fold CV),
extracts confusion matrix and feature importances, and persists best model pipeline.
"""

import os
import json
import sqlite3
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
from sklearn.pipeline import Pipeline

from ml.preprocessing import (
    build_preprocessor, NUMERIC_FEATURES, CATEGORICAL_FEATURES, get_feature_names
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "campustrack.db")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")
MODEL_SAVE_PATH = os.path.join(MODELS_DIR, "placement_model.joblib")

os.makedirs(MODELS_DIR, exist_ok=True)

def load_data():
    """Loads student records from SQLite database, falls back to CSV."""
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM students"
        df = pd.read_sql_query(query, conn)
        conn.close()
    else:
        csv_path = os.path.join(BASE_DIR, "datasets", "sample_students.csv")
        df = pd.read_csv(csv_path)

    # Define binary target: Placed = 1, otherwise = 0
    df["target"] = (df["placement_status"] == "Placed").astype(int)
    return df

def train_and_evaluate_all():
    df = load_data()
    print(f"Loaded {len(df)} total student records. Target distribution: {df['target'].value_counts().to_dict()}")

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X = df[feature_cols]
    y = df["target"]

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    models_config = {
        "Logistic Regression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
    }

    results = {}
    best_model_name = None
    best_f1 = -1.0
    best_pipeline = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, clf in models_config.items():
        preprocessor = build_preprocessor()
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])

        # Cross-validation scores on training data
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1")
        cv_mean = float(np.mean(cv_scores))
        cv_std = float(np.std(cv_scores))

        # Train pipeline
        pipeline.fit(X_train, y_train)

        # Test set predictions
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_test, y_prob))

        # Confusion matrix: [[TN, FP], [FN, TP]]
        cm = confusion_matrix(y_test, y_pred).tolist()

        # ROC Curve sample points for charting (downsampled to 20 points for smooth frontend chart)
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_pts = [
            {"fpr": round(float(f), 3), "tpr": round(float(t), 3)}
            for f, t in zip(fpr[::max(1, len(fpr)//20)], tpr[::max(1, len(tpr)//20)])
        ]
        if roc_pts[-1]["fpr"] != 1.0:
            roc_pts.append({"fpr": 1.0, "tpr": 1.0})

        # Feature importances
        feature_names = get_feature_names(pipeline.named_steps["preprocessor"])
        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
        elif hasattr(clf, "coef_"):
            importances = np.abs(clf.coef_[0])
        else:
            importances = np.zeros(len(feature_names))

        # Normalize and sort feature importances
        total_imp = np.sum(importances)
        if total_imp > 0:
            importances = importances / total_imp

        feat_imp_list = [
            {"feature": fname, "importance": round(float(imp), 4)}
            for fname, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        ]

        results[name] = {
            "name": name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "cv_f1_mean": round(cv_mean, 4),
            "cv_f1_std": round(cv_std, 4),
            "confusion_matrix": {
                "true_negative": cm[0][0],
                "false_positive": cm[0][1],
                "false_negative": cm[1][0],
                "true_positive": cm[1][1]
            },
            "roc_curve": roc_pts,
            "feature_importance": feat_imp_list[:10]  # Top 10
        }

        print(f"[{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f} | 5-Fold CV F1: {cv_mean:.4f}")

        # Best model selection based on test F1 and AUC
        composite_score = f1 * 0.6 + auc * 0.4
        if composite_score > best_f1:
            best_f1 = composite_score
            best_model_name = name
            best_pipeline = pipeline

    print(f"\n>> Selected Best Model: {best_model_name} (Composite Score: {best_f1:.4f})")

    # Fit best model on entire dataset for maximum inference capability in production
    best_pipeline.fit(X, y)

    # Persist model
    joblib.dump(best_pipeline, MODEL_SAVE_PATH)
    print(f"Saved best pipeline model to {MODEL_SAVE_PATH}")

    # Metadata payload
    metadata = {
        "best_model": best_model_name,
        "trained_samples": len(df),
        "test_samples": len(X_test),
        "train_samples": len(X_train),
        "features_used": feature_cols,
        "models": results,
        "disclaimer": "Predictions are probabilistic estimates generated by trained machine learning models for guidance and training prioritization. They do not constitute guaranteed placement outcomes."
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved evaluation metrics to {METRICS_PATH}")

    return metadata

if __name__ == "__main__":
    train_and_evaluate_all()

