# PROJECT REPORT

# CampusTrack AI: College Placement and Student Performance Tracker
**A Predictive Machine Learning and Institutional Analytics Platform**

**Degree**: Bachelor of Technology / Bachelor of Engineering in Computer Science & Engineering / Information Technology / Data Science  
**Academic Year**: 2025–2026  
**Status**: Completed and Verified

---

## CERTIFICATE OF ORIGINALITY & APPROVAL

This is to certify that the project entitled **"CampusTrack AI – College Placement and Student Performance Tracker"** is a bonafide record of independent project work executed to fulfill academic graduation requirements. The design, implementation, evaluation metrics, and machine learning pipeline are original and have been verified under automated testing and cross-validation procedures.

---

## ACKNOWLEDGEMENT

We express our gratitude to the department faculty, project guide, and academic mentors for their constructive feedback and continuous direction throughout the design, architectural modeling, machine learning benchmarking, and user experience validation of this project.

---

## ABSTRACT

Campus recruitment drives are critical milestones for academic institutions and student career progressions. Traditional placement tracking relies primarily on retrospective spreadsheets and manual record-keeping after placement seasons finish, which precludes timely academic intervention for at-risk candidates.

**CampusTrack AI** addresses this limitation by delivering an integrated, full-stack predictive placement platform. The system combines:
1. Longitudinal academic semester tracking (SGPA variations and attendance monitoring).
2. Multi-dimensional employability assessments (quantitative aptitude, technical proficiency, verbal communication, and hands-on programming scores).
3. Supervised classification machine learning models (Logistic Regression, Random Forest, and Gradient Boosting).

The models estimate real-time placement probabilities while strictly excluding post-placement variables to prevent data leakage. Students are categorized into *Placement Ready*, *Developing*, and *Needs Improvement*, and the system automatically synthesizes personalized 30-day action plans and recommended courses. Evaluated on a stratified held-out test dataset, the selected regularized Logistic Regression pipeline achieves an **Accuracy of 83.3%**, an **F1-Score of 85.1%**, and an **ROC-AUC of 0.893**.

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background
Higher educational institutions in engineering and applied sciences are evaluated heavily by accrediting councils (such as NBA and NAAC) on graduate placement percentages, median salary packages, and employer satisfaction. Consequently, universities require intelligent tools capable of forecasting student outcomes early in the 6th or 7th semester rather than reacting after campus drives conclude.

### 1.2 Problem Statement
Existing placement administration faces several key shortcomings:
- **Disparate Records**: Student academic records (marks/grades) and placement assessment records (mock tests, coding scores) are isolated in separate files.
- **Absence of Predictive Analytics**: Placement cells lack automated statistical models to compute individual placement readiness probabilities.
- **Delayed Remedial Action**: Students with declining academic trajectories or specific skill deficiencies (e.g., low aptitude test scores or zero internship experience) are identified too late.
- **Lack of Actionable Guidance**: Generic advice is given to students rather than tailored roadmaps addressing their specific weaknesses.

### 1.3 Project Objectives
1. Implement a unified relational database schema for student academic, assessment, and placement history.
2. Develop a clean RESTful backend API in Python Flask with role-based access control (Admin & Faculty).
3. Train, cross-validate, and benchmark three classification algorithms to predict placement outcomes.
4. Construct an interactive diagnostic simulator providing placement probabilities, risk gaps, and 30-day action plans.
5. Deliver a modern, accessible web dashboard with responsive Recharts visualizations and CSV/Excel import/export capabilities.

---

## CHAPTER 2: LITERATURE SURVEY & COMPARATIVE ANALYSIS

| Approach / Research | Strengths | Limitations | CampusTrack AI Advancement |
|---|---|---|---|
| **Traditional ERP Systems** | Stores student attendance and marks | Purely retrospective; zero predictive or ML capabilities | Adds real-time scikit-learn classification pipeline |
| **Heuristic Score Cutoffs** | Simple rule-based filtering (e.g., CGPA > 7.0) | Ignores multi-variable correlations (internships, coding skills) | Multivariate statistical modeling with probability log-odds |
| **Black-Box Deep Learning** | High fitting capacity on very large datasets | Uninterpretable; prone to severe overfitting on tabular data | Interpretable regularized models with feature importance weights |

---

## CHAPTER 3: SYSTEM ARCHITECTURE & DESIGN

### 3.1 Tiered Architecture
CampusTrack AI follows a decoupled four-tier architecture:
1. **Client / Presentation Layer**: Built with React 19, Vite, and Tailwind CSS v4. Features Lucide iconography, Recharts SVG analytics, and responsive Dark/Light themes.
2. **Application / REST API Layer**: Python Flask 3.1 with blueprint modularization (`auth`, `students`, `dashboard`, `analytics`, `ml`, `dataset`, `reports`).
3. **Machine Learning Pipeline Layer**: Scikit-Learn pipeline encapsulating median imputation, `StandardScaler`, `OneHotEncoder`, and trained classification estimators.
4. **Data Persistence Layer**: SQLite 3 database structured with foreign keys, cascading deletions, and B-tree indexes.

### 3.2 Relational Database Schema
- **`users`**: Manages Admin and Faculty credentials with PBKDF2 password hashes and JWT tokens.
- **`students`**: Master student record containing 23 attributes (identification, demographics, academics, skills, and placement outcomes).
- **`semester_records`**: Captures semester-wise SGPA (Sem 1 through 8), attendance, and backlog counts for trajectory analysis.
- **`dataset_logs`**: Logs file upload history, row counts, and schema validation states.

---

## CHAPTER 4: MACHINE LEARNING PIPELINE & MATHEMATICAL FOUNDATIONS

### 4.1 Feature Selection & Data Leakage Prevention
To guarantee valid inference, post-placement variables (`placement_status`, `company_name`, `job_role`, `salary_package`) are strictly excluded from the feature matrix $X$.

**Input Feature Vector $X$**:
- Numerical: $\text{CGPA}, \text{Attendance}, \text{Backlogs}, \text{Aptitude}, \text{Technical}, \text{Communication}, \text{Coding Rating}, \text{Projects}, \text{Certs}, \text{Internships}, \text{Soft Skills}$.
- Categorical: $\text{Department}$ (One-Hot Encoded).

### 4.2 Mathematical Formulations

#### 1. Logistic Regression Log-Odds & Sigmoid Probability
The linear predictor $\eta$ is modeled as:
$$\eta = \beta_0 + \sum_{j=1}^{p} \beta_j X_j$$
The estimated placement probability $P(\text{Placed} = 1 \mid X)$ is given by:
$$P(Y = 1 \mid X) = \sigma(\eta) = \frac{1}{1 + e^{-\eta}}$$

#### 2. Model Evaluation Metrics
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}, \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
$$\text{ROC-AUC} = \int_{0}^{1} \text{TPR}(\text{FPR}) \, d(\text{FPR})$$

### 4.3 Benchmark Comparison
Evaluated on the held-out stratified 20% test dataset (90 students):

| Model Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV F1 |
|---|---|---|---|---|---|---|
| **Logistic Regression (Selected)** | **83.33%** | **81.13%** | **89.58%** | **85.15%** | **0.8929** | **80.05%** |
| Random Forest Classifier | 81.11% | 78.18% | 89.58% | 83.50% | 0.8487 | 82.29% |
| Gradient Boosting Classifier | 78.89% | 78.43% | 83.33% | 80.81% | 0.8447 | 78.72% |

---

## CHAPTER 5: SOFTWARE TESTING & VALIDATION

Automated unit and integration testing was executed using `pytest`:
- **API Tests (`tests/test_api.py`)**: Validates authentication, JWT validation, KPI calculation accuracy, student CRUD operations, prediction endpoints, and export downloads.
- **ML Pipeline Tests (`tests/test_ml.py`)**: Tests pipeline serialization (`joblib`), schema invariance, high-potential candidate classification, and at-risk candidate classification.
- **Test Results**: 13 of 13 tests passed cleanly with 100% test success rate.

---

## CHAPTER 6: CONCLUSION & FUTURE SCOPE

### 6.1 Conclusion
CampusTrack AI provides an end-to-end, dependable solution for university placement cells. By combining machine learning inference with responsive visual dashboards, institutions can detect at-risk students semesters in advance and tailor interventions that maximize placement conversion rates.

### 6.2 Future Scope
1. **Natural Language Resume Parsing**: Integrate PDF resume parsing to extract technical skills and project keywords automatically.
2. **Company-Specific Fit Predictors**: Extend binary placement prediction into multi-output models predicting fit for specific recruiters (e.g. Dream vs Regular tiers).
3. **Automated WhatsApp / Email Alerts**: Trigger automated milestone notifications to mentors when a student's SGPA drops below threshold.

