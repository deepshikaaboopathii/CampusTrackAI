"""
CampusTrack AI - Realistic Synthetic Dataset Generator
Generates realistic, statistically correlated student performance and placement records.
Disclaimer: This synthetic dataset is generated for demonstration, modeling, and testing.
It models realistic correlations (CGPA, technical, aptitude, internships, etc.)
without containing real private student data.
"""

import os
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

FIRST_NAMES = [
    "Aarav", "Aditi", "Ananya", "Aryan", "Ayush", "Bhavya", "Chetan", "Deepak",
    "Devika", "Dhruv", "Divya", "Gaurav", "Harsh", "Isha", "Ishaan", "Kavya",
    "Kunal", "Meera", "Neha", "Nikhil", "Pooja", "Pranav", "Priya", "Rahul",
    "Rhea", "Rohan", "Saanvi", "Sahil", "Sakshi", "Siddharth", "Sneha", "Tanvi",
    "Utkarsh", "Varun", "Vidya", "Vikram", "Yash", "Zoya", "Aditya", "Akash"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Mehta", "Iyer", "Nair", "Gupta",
    "Chopra", "Deshmukh", "Joshi", "Bhat", "Rao", "Kulkarni", "Singh", "Kumar",
    "Das", "Banerjee", "Pillai", "Menon", "Kapoor", "Malhotra", "Saxena", "Agarwal"
]

DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Electronics & Comm",
    "Data Science & AI",
    "Mechanical"
]

COMPANIES = [
    {"name": "Google", "roles": ["Software Engineer", "Cloud Associate"], "tier": "Super Dream", "min_ctc": 22.0, "max_ctc": 32.0},
    {"name": "Microsoft", "roles": ["Software Dev Engineer", "Support Engineer"], "tier": "Super Dream", "min_ctc": 20.0, "max_ctc": 28.0},
    {"name": "Amazon", "roles": ["SDE I", "Data Engineer", "Operations"], "tier": "Super Dream", "min_ctc": 18.0, "max_ctc": 26.0},
    {"name": "Cisco", "roles": ["Network Engineer", "Systems Engineer"], "tier": "Dream", "min_ctc": 12.0, "max_ctc": 17.0},
    {"name": "Oracle", "roles": ["Database Developer", "Cloud Analyst"], "tier": "Dream", "min_ctc": 11.0, "max_ctc": 16.0},
    {"name": "Deloitte", "roles": ["Technology Analyst", "Consultant"], "tier": "Dream", "min_ctc": 7.5, "max_ctc": 11.0},
    {"name": "Accenture", "roles": ["Associate Software Engineer", "Advanced Analyst"], "tier": "Regular", "min_ctc": 4.5, "max_ctc": 6.5},
    {"name": "TCS", "roles": ["Ninja Developer", "Digital Innovator"], "tier": "Regular", "min_ctc": 3.8, "max_ctc": 7.2},
    {"name": "Infosys", "roles": ["Systems Engineer", "Specialist Programmer"], "tier": "Regular", "min_ctc": 3.8, "max_ctc": 8.0},
    {"name": "Wipro", "roles": ["Project Engineer", "Turbo Dev"], "tier": "Regular", "min_ctc": 3.6, "max_ctc": 6.5},
    {"name": "Cognizant", "roles": ["Programmer Analyst", "GenC Next"], "tier": "Regular", "min_ctc": 4.0, "max_ctc": 6.8},
    {"name": "Zomato", "roles": ["Backend Developer", "Product Operations"], "tier": "Dream", "min_ctc": 10.0, "max_ctc": 15.0}
]

def generate_student_records(count=450):
    records = []
    sem_records = []
    
    dept_codes = {
        "Computer Science": "CS",
        "Information Technology": "IT",
        "Electronics & Comm": "EC",
        "Data Science & AI": "DS",
        "Mechanical": "ME"
    }

    for i in range(1, count + 1):
        dept = random.choice(DEPARTMENTS)
        code = dept_codes[dept]
        
        # Batch split: 60% 2021-2025 (graduating), 40% 2022-2026 (pre-final)
        is_graduating = random.random() < 0.65
        batch = "2021-2025" if is_graduating else "2022-2026"
        grad_year = 2025 if is_graduating else 2026
        
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        student_id = f"CT{grad_year}{code}{i:03d}"
        email = f"{first.lower()}.{last.lower()}{i:03d}@campus.edu"
        gender = random.choices(["Male", "Female", "Other"], weights=[0.55, 0.43, 0.02])[0]
        
        # Latent student baseline ability factor (-2 to +2)
        ability = np.random.normal(0, 1.0)
        
        # Correlated feature generation
        cgpa = np.clip(np.round(7.5 + ability * 0.9 + np.random.normal(0, 0.35), 2), 5.10, 9.95)
        attendance = np.clip(np.round(82.0 + ability * 6.0 + np.random.normal(0, 4.5), 1), 60.0, 99.0)
        
        # Backlog probability higher for lower ability
        if ability < -1.2:
            backlogs = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
        elif ability < -0.5:
            backlogs = random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15])[0]
        else:
            backlogs = random.choices([0, 1], weights=[0.92, 0.08])[0]
            
        aptitude = np.clip(np.round(70.0 + ability * 12.0 + np.random.normal(0, 7.0), 1), 32.0, 99.0)
        technical = np.clip(np.round(68.0 + ability * 14.0 + np.random.normal(0, 6.5), 1), 30.0, 100.0)
        comm = np.clip(np.round(72.0 + ability * 8.0 + np.random.normal(0, 8.0), 1), 35.0, 98.0)
        
        # Programming rating (1.0 to 5.0)
        prog_base = 3.0 + ability * 0.75 + (0.3 if dept in ["Computer Science", "Data Science & AI"] else 0.0)
        programming_rating = np.clip(np.round(prog_base + np.random.normal(0, 0.3), 1), 1.0, 5.0)
        
        # Projects, certs, internships
        projects_count = int(np.clip(np.round(2.5 + ability * 0.9 + np.random.normal(0, 0.8)), 0, 7))
        certifications_count = int(np.clip(np.round(2.0 + ability * 0.7 + np.random.normal(0, 0.8)), 0, 6))
        
        if ability > 0.8:
            internships_count = random.choices([1, 2, 3], weights=[0.4, 0.45, 0.15])[0]
        elif ability > -0.2:
            internships_count = random.choices([0, 1, 2], weights=[0.45, 0.45, 0.1])[0]
        else:
            internships_count = random.choices([0, 1], weights=[0.85, 0.15])[0]
            
        soft_skills = np.clip(np.round(72.0 + ability * 7.0 + np.random.normal(0, 6.0), 1), 40.0, 98.0)
        
        # Eligibility criteria: CGPA >= 6.0 and backlogs <= 1 and attendance >= 70%
        placement_eligible = 1 if (cgpa >= 6.0 and backlogs <= 1 and attendance >= 70.0) else 0
        
        # Placement logic (realistic logistic threshold)
        logit = (
            (cgpa - 7.0) * 0.9 +
            (technical - 65.0) * 0.05 +
            (aptitude - 65.0) * 0.04 +
            (comm - 65.0) * 0.03 +
            (programming_rating - 2.5) * 0.8 +
            internships_count * 0.9 +
            projects_count * 0.25 -
            backlogs * 1.6 +
            (0.3 if dept in ["Computer Science", "Information Technology", "Data Science & AI"] else -0.1)
        )
        placement_prob = 1.0 / (1.0 + np.exp(-logit))
        
        if not placement_eligible:
            placement_status = "Not Placed"
            company_name = None
            job_role = None
            salary_package = None
        else:
            if is_graduating:
                is_placed = (random.random() < placement_prob)
                if is_placed:
                    placement_status = "Placed"
                    # Determine company tier based on scores
                    composite_score = technical * 0.35 + aptitude * 0.25 + cgpa * 10 * 0.25 + internships_count * 5
                    if composite_score > 78 and random.random() < 0.6:
                        company_candidates = [c for c in COMPANIES if c["tier"] == "Super Dream"]
                    elif composite_score > 62:
                        company_candidates = [c for c in COMPANIES if c["tier"] in ["Dream", "Super Dream"]]
                    else:
                        company_candidates = [c for c in COMPANIES if c["tier"] == "Regular"]
                        
                    comp = random.choice(company_candidates)
                    company_name = comp["name"]
                    job_role = random.choice(comp["roles"])
                    salary_package = round(random.uniform(comp["min_ctc"], comp["max_ctc"]), 2)
                else:
                    placement_status = "Not Placed"
                    company_name = None
                    job_role = None
                    salary_package = None
            else:
                # Pre-final batch: some in process, few early placements, rest not placed yet
                if placement_prob > 0.75 and random.random() < 0.4:
                    placement_status = "Placed"
                    comp = random.choice(COMPANIES)
                    company_name = comp["name"]
                    job_role = random.choice(comp["roles"])
                    salary_package = round(random.uniform(comp["min_ctc"], comp["max_ctc"]), 2)
                elif placement_prob > 0.5:
                    placement_status = "In Process"
                    company_name = None
                    job_role = None
                    salary_package = None
                else:
                    placement_status = "Not Placed"
                    company_name = None
                    job_role = None
                    salary_package = None

        student_rec = {
            "student_id": student_id,
            "name": name,
            "email": email,
            "gender": gender,
            "department": dept,
            "batch": batch,
            "graduation_year": grad_year,
            "cgpa": cgpa,
            "attendance": attendance,
            "backlog_count": backlogs,
            "aptitude_score": aptitude,
            "technical_score": technical,
            "communication_score": comm,
            "programming_rating": programming_rating,
            "projects_count": projects_count,
            "certifications_count": certifications_count,
            "internships_count": internships_count,
            "soft_skills_score": soft_skills,
            "placement_eligible": placement_eligible,
            "placement_status": placement_status,
            "company_name": company_name,
            "job_role": job_role,
            "salary_package": salary_package
        }
        records.append(student_rec)
        
        # Generate 6 to 8 semester records
        num_sems = 8 if is_graduating else 6
        # Generate realistic trajectory: improving, fluctuating, or declining
        trajectory_type = random.choices(["steady", "improving", "declining", "volatile"], weights=[0.55, 0.20, 0.15, 0.10])[0]
        cur_sgpa = cgpa
        for sem in range(1, num_sems + 1):
            if trajectory_type == "improving":
                sem_sgpa = cur_sgpa - (num_sems - sem) * 0.15 + np.random.normal(0, 0.18)
            elif trajectory_type == "declining":
                sem_sgpa = cur_sgpa + (num_sems - sem) * 0.18 + np.random.normal(0, 0.2)
            else:
                sem_sgpa = cur_sgpa + np.random.normal(0, 0.25)
            sem_sgpa = float(np.clip(np.round(sem_sgpa, 2), 4.5, 10.0))
            sem_att = float(np.clip(np.round(attendance + np.random.normal(0, 3.5), 1), 55.0, 100.0))
            sem_backlogs = 1 if (backlogs > 0 and sem in [3, 4, 5] and random.random() < 0.5) else 0
            sem_records.append({
                "student_id": student_id,
                "semester": sem,
                "sgpa": sem_sgpa,
                "attendance_pct": sem_att,
                "backlogs": sem_backlogs
            })
            
    df_students = pd.DataFrame(records)
    df_semesters = pd.DataFrame(sem_records)
    return df_students, df_semesters

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datasets_dir = os.path.join(base_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)
    
    df_students, df_semesters = generate_student_records(450)
    
    # Save student dataset
    students_csv_path = os.path.join(datasets_dir, "sample_students.csv")
    df_students.to_csv(students_csv_path, index=False)
    print(f"Generated {len(df_students)} student records at {students_csv_path}")
    
    # Save semester dataset
    semesters_csv_path = os.path.join(datasets_dir, "sample_semesters.csv")
    df_semesters.to_csv(semesters_csv_path, index=False)
    print(f"Generated {len(df_semesters)} semester records at {semesters_csv_path}")
    
    # Create sample template CSV with empty rows/examples for users to download
    template_cols = [
        "student_id", "name", "email", "gender", "department", "batch",
        "graduation_year", "cgpa", "attendance", "backlog_count",
        "aptitude_score", "technical_score", "communication_score",
        "programming_rating", "projects_count", "certifications_count",
        "internships_count", "soft_skills_score", "placement_eligible",
        "placement_status", "company_name", "job_role", "salary_package"
    ]
    df_template = df_students.head(5).copy()
    template_path = os.path.join(datasets_dir, "sample_template.csv")
    df_template.to_csv(template_path, index=False)
    print(f"Sample template created at {template_path}")

if __name__ == "__main__":
    main()
