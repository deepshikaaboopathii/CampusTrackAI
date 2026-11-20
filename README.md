# CampusTrack AI – College Placement and Student Performance Tracker

**CampusTrack AI** is an enterprise-grade full-stack web application designed for engineering colleges and universities to monitor student academic performance, analyze placement readiness, predict placement outcomes using machine learning classification pipelines, and identify students requiring targeted training and remedial intervention.

---

## 1. Key Features & Modules

### 1. Executive Analytics Dashboard
- **Comprehensive KPI Tracking**: Real-time computation of Total Students, Placed Count, Placement Percentage, Eligibility Count, Students Requiring Training, Average CGPA, Assessment Benchmarks (Technical & Aptitude), and Compensation Packages (Average, Min, Max LPA).
- **Interactive Visualizations (Recharts)**:
  - Department-wise placement success rates (Bar Chart).
  - Placed vs. Unplaced vs. In-Process outcome breakdown (Donut Chart).
  - Compensation package distribution across CTC tiers (Bar Chart).
  - Institutional semester-by-semester SGPA progression (Line Chart).
  - Cross-department technical and aptitude score benchmarks.
- **Dynamic Filtering**: Instant recalculation across Department, Batch, and Graduation Year filters.

### 2. Student Management System
- **Full CRUD Support**: Add, view, edit, and delete student records with relational integrity.
- **Rich Student Profiles**: In-depth personal details, academic metrics, semester trajectory charts, skill radar charts, placement status, company offer details, and instant AI readiness diagnostics.
- **Search & Multi-Filter Querying**: Filter by department, batch, CGPA bracket, placement status, and eligibility, with sortable columns and pagination.

### 3. Academic & Employability Analytics
- **Performance Correlations**: Attendance vs. CGPA scatter plots, aptitude vs. technical assessment comparisons, and CGPA distribution histograms.
- **At-Risk Identification**: Automated detection of students exhibiting declining academic trajectories (e.g. drops in semester SGPA).
- **High-Potential Talent Identification**: Surfaces top candidates ready for Super Dream company recruitment drives.
- **Cross-Department Skill Matrix**: Evaluates strengths in coding, technical knowledge, aptitude, and communication across engineering departments.

### 4. Machine Learning: Placement Prediction Pipeline
- **Algorithms Implemented & Compared**:
  1. **Logistic Regression** (L2 regularized, calibrated)
  2. **Random Forest Classifier** (Ensemble tree voting with Gini impurity)
  3. **Gradient Boosting Classifier** (Sequential error reduction)
- **Strict Data Leakage Prevention**: Post-placement outcomes (company, salary, placed status) are strictly excluded from feature inputs.
- **Preprocessing Pipeline**: Missing value imputation, robust numeric scaling, and one-hot encoding for categorical domain attributes.
- **Validation**: Stratified 80/20 train/test split, 5-Fold Cross-Validation, Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix, and Feature Importance rankings.
- **Automated Model Selection & Persistence**: Dynamically exports the best performing model pipeline (`placement_model.joblib`) and metrics report (`model_metrics.json`).
- **Dynamic In-App Model Retraining**: Retrain the model on current database records directly via the frontend UI.

### 5. Individual Placement Readiness Analyzer
- **Interactive Sandbox**: Adjust CGPA, attendance, backlogs, aptitude, technical score, communication, coding rating, internships, projects, and certifications.
- **One-Click Presets**: Test archetypes like *"High Achiever"*, *"Average Candidate"*, *"Needs Support"*, and *"Coder Low CGPA"*.
- **Comprehensive Output**:
  - Estimated Placement Probability (%).
  - Readiness Category: **Placement Ready**, **Developing**, or **Needs Improvement**.
  - Pinpointed Academic Strengths & Key Risk Gaps.
  - Personalized 30-Day Action Roadmap (Days 1-10, 11-20, 21-30).
  - Recommended Courses with estimated completion hours.
  - Transparent ML probabilistic disclaimer.

### 6. Dataset Management & Ingestion
- Upload `.csv` or `.xlsx` datasets.
- Schema verification, missing value detection, and duplicate roll ID flagging against the database.
- Interactive data preview before database import.
- Downloadable sample CSV template and database export.

### 7. Institutional Reports & Exports
- Executive Placement Dossier with department summaries and key hiring partner statistics.
- Remedial Training Dossier listing at-risk students with specific intervention triggers.
- Printable view and one-click CSV exports.

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS (v4), Lucide React Icons, Recharts, Axios, React Router v7 |
| **Backend** | Python Flask 3.1, RESTful API architecture, SQLite 3, PyJWT |
| **Data Science & ML** | Scikit-learn, Pandas, NumPy, Scipy, Joblib, Openpyxl |
| **Testing** | Pytest, Flask Test Client |

---

## 3. Project Structure

```
campus-track-ai/
├── backend/
│   ├── app.py                      # Flask application factory and CORS configuration
│   ├── config.py                   # Application configurations and upload settings
│   ├── database/
│   │   ├── campustrack.db          # SQLite database file
│   │   ├── db.py                   # SQLite connection context managers and schema init
│   │   ├── schema.sql              # Relational SQL schema definitions and indexes
│   │   └── seed.py                 # Database seeder with realistic records
│   ├── routes/
│   │   ├── auth_routes.py          # Authentication endpoints (login, register, me)
│   │   ├── dashboard_routes.py     # Aggregated KPI and chart metrics
│   │   ├── student_routes.py       # CRUD operations, filtering, pagination
│   │   ├── analytics_routes.py     # Academic and placement analytics endpoints
│   │   ├── ml_routes.py            # Real-time prediction, metrics, retraining
│   │   ├── dataset_routes.py       # File validation, upload, import, export
│   │   └── report_routes.py        # Executive and remedial reports
│   └── services/
│       ├── auth_service.py         # JWT tokens and password hashing (PBKDF2/sha256)
│       ├── student_service.py      # Database query logic, pagination, sorting
│       ├── analytics_service.py    # Analytical aggregations and correlation calculations
│       └── dataset_service.py      # Tabular file validation, upserting, and export
├── ml/
│   ├── dataset_generator.py        # Realistic synthetic dataset generator
│   ├── preprocessing.py            # Feature definitions and scikit-learn transformers
│   ├── train_model.py              # 3-model comparative training, CV, metrics persistence
│   ├── predict.py                  # Real-time inference, readiness categorizer, roadmap
│   └── models/
│       ├── placement_model.joblib  # Trained scikit-learn model pipeline
│       └── model_metrics.json      # Model benchmark metrics and ROC/confusion matrix data
├── datasets/
│   ├── sample_students.csv         # 450 realistic student records
│   ├── sample_semesters.csv        # 3,200+ semester performance records
│   └── sample_template.csv         # Standard CSV upload template
├── frontend/
│   ├── src/
│   │   ├── api/client.js           # Axios API service client
│   │   ├── context/
│   │   │   ├── AuthContext.jsx     # User authentication state and roles
│   │   │   └── ThemeContext.jsx    # Dark / Light theme toggle
│   │   ├── components/
│   │   │   ├── Header.jsx          # Top bar with user profile and theme switch
│   │   │   ├── Sidebar.jsx         # Collapsible responsive navigation drawer
│   │   │   ├── MetricCard.jsx      # Reusable KPI card with badge and trend
│   │   │   ├── StatusBadge.jsx     # Colored pill badges for statuses and readiness
│   │   │   ├── LoadingSkeleton.jsx # Responsive pulse placeholder loader
│   │   │   ├── StudentModal.jsx    # Add / Edit student form modal
│   │   │   ├── StudentProfileModal.jsx # Detailed student profile and radar analytics
│   │   │   └── LoginModal.jsx      # Authentication modal with demo presets
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx   # Main executive placement overview
│   │   │   ├── StudentsPage.jsx    # Student directory with search, filter, sort
│   │   │   ├── AcademicAnalyticsPage.jsx # Academic correlations, at-risk rosters
│   │   │   ├── PlacementAnalyticsPage.jsx# Company recruitment volume, CTC charts
│   │   │   ├── PredictorPage.jsx   # Interactive AI placement readiness analyzer
│   │   │   ├── ModelEvaluationPage.jsx # ML model comparison, ROC, confusion matrix
│   │   │   ├── DatasetPage.jsx     # CSV/XLSX file validation, preview, import
│   │   │   └── ReportsPage.jsx     # Institutional dossiers and CSV exports
│   │   ├── App.jsx                 # Route definitions and layout wrapper
│   │   ├── index.css               # Tailwind CSS imports and custom styling
│   │   └── main.jsx                # React DOM entry point
│   └── vite.config.js              # Vite bundler configuration with proxy
├── tests/
│   ├── test_api.py                 # Backend API endpoint test suite
│   └── test_ml.py                  # ML pipeline, preprocessing, and inference tests
├── requirements.txt                # Python package dependencies
├── run_app.bat                     # Windows one-click launcher for Frontend and Backend
├── run_backend.bat                 # Windows launcher for Flask API
├── run_frontend.bat                # Windows launcher for Vite frontend
└── README.md                       # Comprehensive project documentation
```

---

## 4. Setup & Installation Instructions

### Prerequisites
- **Python**: Version 3.10+ (Recommended: Python 3.12)
- **Node.js**: Version 18+ (Recommended: Node 20 or 24)
- **npm** or **pnpm**

---

### Step 1: Install Python Dependencies
Open PowerShell or Command Prompt in the project root directory:
```bash
py -3.12 -m pip install -r requirements.txt
```

---

### Step 2: Initialize Database & Seed Realistic Dataset
Generate the realistic student dataset and seed the SQLite database:
```bash
# Generate synthetic dataset (450 students, 3,200+ semester records)
py -3.12 ml/dataset_generator.py

# Seed the database
py -3.12 -m backend.database.seed
```

---

### Step 3: Train and Evaluate Machine Learning Pipeline
Train the classification models (Logistic Regression, Random Forest, Gradient Boosting) and evaluate their performance:
```bash
py -3.12 -m ml.train_model
```
*This command generates `ml/models/placement_model.joblib` and `ml/models/model_metrics.json`.*

---

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 5. Running the Application

### Option A: One-Click Windows Batch Launcher
Double-click `run_app.bat` or run from terminal:
```cmd
run_app.bat
```
This opens two windows:
1. **Flask Backend**: `http://127.0.0.1:5000`
2. **React Frontend**: `http://localhost:5173`

---

### Option B: Manual Execution

#### Terminal 1 – Flask Backend:
```bash
py -3.12 -m backend.app
```
*Backend runs at `http://127.0.0.1:5000`.*

#### Terminal 2 – React Frontend:
```bash
cd frontend
npm run dev
```
*Frontend runs at `http://localhost:5173`.*

Open your web browser and navigate to: **`http://localhost:5173`**

---

## 6. Demo Accounts (Role-Based Authentication)

The system is pre-configured with two default accounts:

| Role | Email / Username | Password | Privileges |
|---|---|---|---|
| **Administrator** | `admin@campustrack.ai` (or `admin`) | `Admin@123` | Full access: Add/Edit/Delete students, Upload datasets, Retrain ML models, Export dossiers |
| **Faculty Member** | `faculty@campustrack.ai` (or `faculty`) | `Faculty@123` | View analytics, evaluate students, generate readiness plans, inspect dossiers |

*The login modal features **one-click demo login buttons** to autofill credentials for presentations.*

---

## 7. Machine Learning Pipeline Details

### Input Features
- `cgpa`: Academic performance scale (0 - 10.0)
- `attendance`: Class attendance percentage (0 - 100%)
- `backlog_count`: Number of active standing backlogs
- `aptitude_score`: Quantitative & logical reasoning test score (0 - 100)
- `technical_score`: Domain engineering assessment score (0 - 100)
- `communication_score`: Verbal and interview articulation score (0 - 100)
- `programming_rating`: Practical coding proficiency rating (1.0 - 5.0)
- `projects_count`: Number of completed engineering projects
- `certifications_count`: Verified technical certifications
- `internships_count`: Completed industry internships
- `soft_skills_score`: Behavioral and leadership assessment rating
- `department`: Categorical (Computer Science, IT, ECE, Data Science & AI, Mechanical)

### Evaluation Metrics Summary (Held-out Test Dataset)
| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV (F1) |
|---|---|---|---|---|---|---|
| **Logistic Regression (Selected)** | **83.3%** | **81.1%** | **89.6%** | **85.1%** | **0.893** | **80.1%** |
| Random Forest Classifier | 81.1% | 78.2% | 89.6% | 83.5% | 0.849 | 82.3% |
| Gradient Boosting Classifier | 78.9% | 78.4% | 83.3% | 80.8% | 0.845 | 78.7% |

*Disclaimer: Predictions are probabilistic estimates generated by trained machine learning models for guidance and training prioritization. They do not constitute guaranteed placement outcomes.*

---

## 8. REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | System health check |
| `/api/auth/login` | POST | Authenticate user and issue JWT |
| `/api/auth/register` | POST | Register faculty or administrator |
| `/api/auth/me` | GET | Fetch authenticated user profile |
| `/api/dashboard/stats` | GET | Aggregated KPIs and chart data with filters |
| `/api/students` | GET | List students with search, sorting, pagination |
| `/api/students` | POST | Create new student profile |
| `/api/students/<id>` | GET | Student profile with semester history & ML diagnostics |
| `/api/students/<id>` | PUT | Update student parameters |
| `/api/students/<id>` | DELETE | Delete student record |
| `/api/students/filters` | GET | Distinct departments, batches, graduation years |
| `/api/analytics/academic`| GET | Academic distributions, correlations, at-risk lists |
| `/api/analytics/placement`| GET | Recruiter volumes, salary distributions, CTC tiers |
| `/api/ml/predict` | POST | Predict placement probability and 30-day action plan |
| `/api/ml/metrics` | GET | ML model benchmarks, confusion matrix, ROC curves |
| `/api/ml/retrain` | POST | Retrain ML pipeline on live database records |
| `/api/dataset/upload` | POST | Validate and preview uploaded CSV/Excel spreadsheet |
| `/api/dataset/commit` | POST | Ingest validated records into database |
| `/api/dataset/template` | GET | Download CSV schema template |
| `/api/dataset/export` | GET | Export student records as CSV |
| `/api/reports/summary` | GET | Executive placement summary dossier |
| `/api/reports/training-needed` | GET | Candidate roster requiring training intervention |

---

## 9. Running Automated Tests

Run the comprehensive test suite covering both Backend REST APIs and Machine Learning Pipelines:
```bash
py -3.12 -m pytest tests/ -v
```
All 13 test suites validate:
- Authentication & JWT token security
- Dashboard KPI calculation integrity
- Student CRUD operations & relational cascading
- ML preprocessing, feature extraction, and model loading
- Prediction inference across high-potential and at-risk profiles
- Tabular export formatting

