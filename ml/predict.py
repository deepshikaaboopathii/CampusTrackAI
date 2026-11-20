"""
CampusTrack AI - Inference & Placement Readiness Engine
Provides real-time placement probability estimation, readiness categorization,
feature contribution breakdown, personalized skill gap analysis, and 30-day action roadmap.
"""

import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "placement_model.joblib")

_model = None

def get_loaded_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            from ml.train_model import train_and_evaluate_all
            train_and_evaluate_all()
        _model = joblib.load(MODEL_PATH)
    return _model

def analyze_student_profile(features: dict) -> dict:
    """
    Predicts placement probability and generates comprehensive readiness diagnostic.
    """
    model = get_loaded_model()

    # Normalize input dictionary with default fallbacks
    row = {
        "department": str(features.get("department", "Computer Science")),
        "cgpa": float(features.get("cgpa", 7.0)),
        "attendance": float(features.get("attendance", 75.0)),
        "backlog_count": int(features.get("backlog_count", 0)),
        "aptitude_score": float(features.get("aptitude_score", 65.0)),
        "technical_score": float(features.get("technical_score", 65.0)),
        "communication_score": float(features.get("communication_score", 65.0)),
        "programming_rating": float(features.get("programming_rating", 3.0)),
        "projects_count": int(features.get("projects_count", 2)),
        "certifications_count": int(features.get("certifications_count", 1)),
        "internships_count": int(features.get("internships_count", 0)),
        "soft_skills_score": float(features.get("soft_skills_score", 70.0))
    }

    df_single = pd.DataFrame([row])

    # Predict probability of placement
    probs = model.predict_proba(df_single)[0]
    placed_prob = float(probs[1]) * 100.0  # In percent

    # Readiness categorization
    if placed_prob >= 75.0:
        readiness_category = "Placement Ready"
        readiness_badge = "success"
        readiness_desc = "The student demonstrates high placement readiness across core academic and employability metrics."
    elif placed_prob >= 48.0:
        readiness_category = "Developing"
        readiness_badge = "warning"
        readiness_desc = "The student shows solid potential with a few identifiable skill gaps that can be strengthened before campus drives."
    else:
        readiness_category = "Needs Improvement"
        readiness_badge = "danger"
        readiness_desc = "Targeted academic and technical intervention is strongly advised to boost placement eligibility and performance."

    # Identify strengths
    strengths = []
    if row["cgpa"] >= 8.2:
        strengths.append(f"Strong Academic Foundation (CGPA {row['cgpa']:.2f}/10)")
    elif row["cgpa"] >= 7.5:
        strengths.append(f"Consistent Academic Standing (CGPA {row['cgpa']:.2f})")

    if row["technical_score"] >= 78:
        strengths.append(f"Advanced Technical Competence ({row['technical_score']:.1f}/100)")
    if row["aptitude_score"] >= 75:
        strengths.append(f"High Quantitative & Logical Aptitude ({row['aptitude_score']:.1f}/100)")
    if row["internships_count"] >= 1:
        strengths.append(f"Practical Industry Exposure ({row['internships_count']} completed internship{'s' if row['internships_count']>1 else ''})")
    if row["programming_rating"] >= 4.0:
        strengths.append(f"Top-Tier Coding Proficiency ({row['programming_rating']:.1f}/5.0)")
    if row["communication_score"] >= 80:
        strengths.append(f"Excellent Communication & Interview Articulation ({row['communication_score']:.1f}/100)")
    if row["projects_count"] >= 3:
        strengths.append(f"Extensive Project Portfolio ({row['projects_count']} projects built)")
    if row["backlog_count"] == 0 and row["attendance"] >= 85:
        strengths.append(f"Impeccable Academic Discipline (0 backlogs, {row['attendance']:.1f}% attendance)")

    if not strengths:
        strengths.append("Foundational understanding across baseline engineering subjects")

    # Identify skill gaps / risk factors
    skill_gaps = []
    if row["backlog_count"] > 0:
        skill_gaps.append(f"Active Backlogs ({row['backlog_count']}): Immediate clearing needed to satisfy corporate cutoff criteria.")
    if row["cgpa"] < 6.5:
        skill_gaps.append(f"CGPA below corporate screening threshold: Minimum 6.5 - 7.0 required by Tier-1 recruiters.")
    if row["aptitude_score"] < 60:
        skill_gaps.append(f"Low Aptitude Score ({row['aptitude_score']:.1f}/100): High risk of disqualification in Round-1 online screening assessments.")
    if row["technical_score"] < 60:
        skill_gaps.append(f"Technical Knowledge Gap ({row['technical_score']:.1f}/100): Needs targeted revision in core domain subjects & data structures.")
    if row["internships_count"] == 0:
        skill_gaps.append("Zero Industry Internships: Practical experiential learning or industry capstone is missing.")
    if row["programming_rating"] < 3.0:
        skill_gaps.append(f"Limited Hands-on Coding Rating ({row['programming_rating']:.1f}/5.0): Insufficient for technical coding rounds.")
    if row["communication_score"] < 65:
        skill_gaps.append(f"Communication & HR Articulation ({row['communication_score']:.1f}/100): Needs mock group discussions and interview practice.")
    if row["attendance"] < 75:
        skill_gaps.append(f"Sub-75% Attendance ({row['attendance']:.1f}%): College placement eligibility policy risk.")

    if not skill_gaps:
        skill_gaps.append("No critical weaknesses detected; focus on advanced domain interview drills and high-tier competitive tracks.")

    # 30-Day Action Roadmap
    roadmap = []
    if row["aptitude_score"] < 70 or row["technical_score"] < 70:
        roadmap.append({
            "phase": "Days 1 - 10",
            "title": "Aptitude & Core Fundamentals Sprint",
            "details": "Practice 40 daily aptitude questions (Speed Math, Syllogisms, Probability). Revise core CS fundamentals (OS, DBMS, Computer Networks)."
        })
    else:
        roadmap.append({
            "phase": "Days 1 - 10",
            "title": "Advanced Problem Solving",
            "details": "Solve 3 medium/hard LeetCode/HackerRank problems daily focusing on Dynamic Programming, Graphs, and Trees."
        })

    if row["internships_count"] == 0 or row["projects_count"] < 2:
        roadmap.append({
            "phase": "Days 11 - 20",
            "title": "Portfolio & Full-Stack Capstone",
            "details": "Build and deploy a full-stack project or industry case study with GitHub documentation, live demo, and automated tests."
        })
    else:
        roadmap.append({
            "phase": "Days 11 - 20",
            "title": "System Design & Project Defense",
            "details": "Deep-dive into architecture, trade-offs, and scaling bottlenecks of previous projects. Practice system design interview scenarios."
        })

    if row["communication_score"] < 75:
        roadmap.append({
            "phase": "Days 21 - 30",
            "title": "HR & Mock Interview Boot Camp",
            "details": "Conduct 5 recorded peer mock interviews using the STAR method for behavioral questions. Practice group discussions on trending tech topics."
        })
    else:
        roadmap.append({
            "phase": "Days 21 - 30",
            "title": "Company-Specific Mock Drills",
            "details": "Solve past recruitment test papers of targeted Super Dream / Dream companies under timed test conditions."
        })

    # Recommended courses / training modules
    recommended_courses = []
    if row["programming_rating"] < 3.5 or row["technical_score"] < 70:
        recommended_courses.append({
            "title": "Data Structures & Algorithms Mastery",
            "category": "Technical",
            "estimated_hours": 35,
            "platform": "CampusTrack LMS / LeetCode"
        })
    if row["aptitude_score"] < 72:
        recommended_courses.append({
            "title": "Campus Placement Quantitative & Reasoning Accelerator",
            "category": "Aptitude",
            "estimated_hours": 24,
            "platform": "AptitudePrep Pro"
        })
    if row["communication_score"] < 75 or row["soft_skills_score"] < 75:
        recommended_courses.append({
            "title": "Corporate Readiness & Behavioral Interviewing (STAR Method)",
            "category": "Soft Skills",
            "estimated_hours": 15,
            "platform": "Campus Finishing School"
        })
    if row["department"] in ["Computer Science", "Information Technology", "Data Science & AI"]:
        recommended_courses.append({
            "title": "Full-Stack Web & Cloud Deployment Essentials",
            "category": "Domain Specialization",
            "estimated_hours": 30,
            "platform": "TechStack Accelerator"
        })
    elif row["department"] == "Electronics & Comm":
        recommended_courses.append({
            "title": "Embedded Systems & IoT Architecture for Core Placements",
            "category": "Domain Specialization",
            "estimated_hours": 30,
            "platform": "HardwareTech Core"
        })
    else:
        recommended_courses.append({
            "title": "CAD/CAM & Industrial Automation Placement Primer",
            "category": "Domain Specialization",
            "estimated_hours": 30,
            "platform": "Core Engineering Lab"
        })

    return {
        "placement_probability": round(placed_prob, 1),
        "readiness_category": readiness_category,
        "readiness_badge": readiness_badge,
        "readiness_description": readiness_desc,
        "strengths": strengths,
        "skill_gaps": skill_gaps,
        "roadmap_30_days": roadmap,
        "recommended_courses": recommended_courses,
        "disclaimer": "Predictions are probabilistic estimates generated by trained machine learning models for guidance and training prioritization. They do not constitute guaranteed placement outcomes."
    }

if __name__ == "__main__":
    # Test sample profile
    test_student = {
        "department": "Computer Science",
        "cgpa": 8.4,
        "attendance": 88.0,
        "backlog_count": 0,
        "aptitude_score": 82.0,
        "technical_score": 85.0,
        "communication_score": 78.0,
        "programming_rating": 4.0,
        "projects_count": 3,
        "certifications_count": 2,
        "internships_count": 1,
        "soft_skills_score": 80.0
    }
    result = analyze_student_profile(test_student)
    print("Inference Test Result:")
    print(f"Probability: {result['placement_probability']}%")
    print(f"Category: {result['readiness_category']}")
    print(f"Strengths: {len(result['strengths'])}")
    print(f"Gaps: {len(result['skill_gaps'])}")

