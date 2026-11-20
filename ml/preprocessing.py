"""
CampusTrack AI - ML Feature Preprocessing Pipeline
Defines feature columns, transformers, and scikit-learn pipeline builder.
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Numerical features
NUMERIC_FEATURES = [
    "cgpa",
    "attendance",
    "backlog_count",
    "aptitude_score",
    "technical_score",
    "communication_score",
    "programming_rating",
    "projects_count",
    "certifications_count",
    "internships_count",
    "soft_skills_score"
]

# Categorical features
CATEGORICAL_FEATURES = [
    "department"
]

# Excluded columns to strictly prevent data leakage and target contamination
EXCLUDED_COLUMNS = [
    "id",
    "student_id",
    "name",
    "email",
    "gender",
    "batch",
    "graduation_year",
    "placement_eligible",
    "placement_status",
    "company_name",
    "job_role",
    "salary_package",
    "created_at",
    "updated_at"
]

def build_preprocessor():
    """
    Builds a ColumnTransformer for preprocessing numeric and categorical features.
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Computer Science")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor

def get_feature_names(preprocessor):
    """Returns the transformed feature names."""
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    cat_features = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    return NUMERIC_FEATURES + cat_features

