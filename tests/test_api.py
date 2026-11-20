import pytest
import json
from backend.app import create_app
from backend.database.seed import seed_database

@pytest.fixture(scope="module")
def client():
    seed_database()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_auth_login_success(client):
    res = client.post("/api/auth/login", json={
        "email": "admin@campustrack.ai",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "token" in data
    assert data["user"]["role"] == "admin"

def test_auth_login_invalid(client):
    res = client.post("/api/auth/login", json={
        "email": "admin@campustrack.ai",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

def test_dashboard_stats(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert "kpis" in data
    assert data["kpis"]["total_students"] > 0
    assert "department_stats" in data
    assert len(data["department_stats"]) > 0

def test_students_listing_and_filter(client):
    res = client.get("/api/students?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["students"]) <= 10
    assert data["pagination"]["total_records"] > 0

def test_student_detail(client):
    res = client.get("/api/students?limit=1")
    first_st = res.get_json()["students"][0]
    detail_res = client.get(f"/api/students/{first_st['student_id']}")
    assert detail_res.status_code == 200
    st_data = detail_res.get_json()
    assert st_data["student_id"] == first_st["student_id"]
    assert "readiness_analysis" in st_data
    assert "radar_metrics" in st_data

def test_ml_predict(client):
    payload = {
        "department": "Computer Science",
        "cgpa": 8.5,
        "attendance": 90.0,
        "backlog_count": 0,
        "aptitude_score": 85.0,
        "technical_score": 88.0,
        "communication_score": 80.0,
        "programming_rating": 4.5,
        "projects_count": 3,
        "certifications_count": 2,
        "internships_count": 1,
        "soft_skills_score": 82.0
    }
    res = client.post("/api/ml/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "placement_probability" in data
    assert data["placement_probability"] >= 0.0
    assert data["readiness_category"] in ["Placement Ready", "Developing", "Needs Improvement"]
    assert len(data["roadmap_30_days"]) > 0

def test_ml_metrics(client):
    res = client.get("/api/ml/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert "models" in data
    assert "Logistic Regression" in data["models"]
    assert "Random Forest" in data["models"]
    assert "Gradient Boosting" in data["models"]

def test_reports_endpoints(client):
    res = client.get("/api/reports/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert "college_name" in data

    res_train = client.get("/api/reports/training-needed")
    assert res_train.status_code == 200
    assert "total_requiring_training" in res_train.get_json()

