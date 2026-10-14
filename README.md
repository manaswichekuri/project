# AI-Powered Insider Threat Detection and Risk Scoring System
### 4th-Year B.Tech CSE Cybersecurity Capstone Project

---

## Executive Summary & Overview
The **AI-Powered Insider Threat Detection and Risk Scoring System** is an end-to-end web application and Security Operations Center (SOC) dashboard designed to detect suspicious insider activity using machine learning behavioral analysis.

Instead of relying solely on static rules or black-box predictions, this system aggregates fine-grained user activity logs, extracts 7 engineered behavioral features, fits an unsupervised **Isolation Forest** anomaly detection model, normalizes anomaly scores into an interpretable **0–100 risk scale**, and generates **human-readable explainability reasons** for security administrators.

> [!NOTE]
> **Academic Prototype Note**: This system is a working academic prototype designed for local demonstration using synthetic dataset generation. It explicitly separates simulated/demo activity from real enterprise monitoring.

---

## Problem Statement & Objectives
### Problem Statement
Enterprise organizations face increasing security risks from insider threats—employees, contractors, or compromised accounts accessing sensitive assets outside their standard baseline behaviors. Traditional rule-based SIEM systems trigger excessive false positives or fail to detect novel exfiltration patterns.

### Objectives
1. **Behavioral Baseline Profiling**: Continuously monitor employee activity logs across file transfers, authentication attempts, device usage, and work hours.
2. **Machine Learning Anomaly Detection**: Deploy an unsupervised Isolation Forest model to detect structural deviations from normal user patterns without needing labeled malicious training data.
3. **Interpretable Risk Scoring**: Transform raw decision scores into a 0–100 normalized risk score categorized into `Low`, `Medium`, `High`, and `Critical`.
4. **Explainable AI (XAI)**: Generate clear, human-understandable reason strings (e.g. *"Unusual after-hours activity"*, *"Download volume 10x above baseline"*) for every detected anomaly.
5. **Interactive SOC Dashboard**: Deliver an Angular Material Security Operations Center interface for security analysts to monitor threats, inspect user risk profiles, and manage alert tickets.

---

## System Architecture

```
                                  +---------------------------------------+
                                  |    Angular 18+ Cyber SOC Dashboard    |
                                  |   (TypeScript, Angular Material)      |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTP / REST API (JSON)
                                                      v
                                  +-------------------+-------------------+
                                  |       Flask REST API Gateway          |
                                  |   (Flask, Flask-CORS, PyMongo)        |
                                  +-------------------+-------------------+
                                                      |
                                      +---------------+---------------+
                                      |                               |
                                      v                               v
                     +----------------+----------------+     +--------+-------+
                     |    Feature Preprocessor &       |     |  MongoDB Store |
                     |   Isolation Forest Pipeline     |     | (Users, Logs,  |
                     +----------------+----------------+     | Risk, Alerts)  |
                                      |                      +----------------+
                                      v
                     +----------------+----------------+
                     |   Interpretable Risk Engine     |
                     |   & Explainability Generator    |
                     +----------------+----------------+
                                      |
                                      v
                     +----------------+----------------+
                     |    Security Alert Dispatcher    |
                     +---------------------------------+
```

---

## Technology Stack

### Frontend
- **Framework**: Angular 18+ (Standalone Components, TypeScript 5.4+)
- **UI Components**: Angular Material 18+, Cyber SOC SCSS Dark Theme
- **Data Visualization**: Chart.js 4.4+ & `ng2-charts`
- **State & Async**: RxJS

### Backend & Machine Learning
- **API Framework**: Python 3.10+, Flask 3.0+, Flask-CORS
- **Machine Learning**: `scikit-learn` (Isolation Forest, StandardScaler), `pandas`, `numpy`
- **Model Serialization**: `joblib`
- **Security & Password Hashing**: `Werkzeug` (PBKDF2/bcrypt)

### Database
- **Primary Store**: MongoDB (PyMongo driver with automatic `mongomock` in-memory fallback)

---

## Repository Folder Structure

```
ai-insider-threat-detection/
│
├── backend/
│   ├── app/
│   │   ├── config/             # Environment & threshold settings
│   │   ├── models/             # Schema specifications
│   │   ├── services/           # Business logic & database operations
│   │   ├── ml/                 # Preprocessor, Isolation Forest, Explainer, Generator
│   │   ├── routes/             # REST API endpoints (Auth, Users, Activity, Risk, Alerts)
│   │   └── utils/              # MongoDB connection & JSON serializers
│   ├── datasets/               # Saved model artifacts & sample datasets
│   ├── tests/                  # Pytest automated test suites
│   ├── requirements.txt        # Python package dependencies
│   ├── .env.example
│   └── run.py                  # Flask server entry point
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/           # Guards, Services (ApiService, AuthService)
│   │   │   ├── models/         # TypeScript interfaces
│   │   │   ├── pages/          # Login, Dashboard, Users, User-Detail, Activity-Logs, Alerts, Analytics, System-Info
│   │   │   └── shared/         # Navbar, Sidebar, MetricCard, RiskBadge
│   │   └── styles.scss         # Cyber SOC Dark Theme
│   ├── angular.json
│   └── package.json
│
├── README.md
└── .gitignore
```

---

## Database Collections & Schemas

### 1. `users`
```json
{
  "user_id": "EMP-1013",
  "name": "Dmitri Ivanov",
  "email": "dmitri.ivanov@enterprise.internal",
  "department": "IT Support",
  "role": "Systems Administrator",
  "baseline_location": "New York, USA",
  "baseline_device": "DEV-EMP-1013",
  "is_demo_synthetic": true
}
```

### 2. `activities`
```json
{
  "activity_id": "ACT-10482",
  "user_id": "EMP-1013",
  "timestamp": "2026-09-18T03:14:00Z",
  "event_type": "FILE_DOWNLOAD",
  "location_ip": "198.51.100.250",
  "location_name": "Moscow, Russia",
  "device_id": "UNREGISTERED-MAC-9482",
  "file_details": {
    "filename": "Customer_SSN_Vault_2026.csv",
    "files_accessed_count": 85,
    "download_size_mb": 1250.0,
    "upload_size_mb": 350.0
  },
  "after_hours": true,
  "failed_logins": 5,
  "is_demo_synthetic": true
}
```

### 3. `risk_scores`
```json
{
  "user_id": "EMP-1013",
  "evaluated_at": "2026-09-18T03:15:00Z",
  "raw_anomaly_score": -0.3842,
  "normalized_risk_score": 92.5,
  "risk_category": "Critical",
  "contributing_reasons": [
    "Unusual after-hours activity (75% of events outside standard hours)",
    "Multiple failed login attempts detected (5 consecutive failures)",
    "Download volume significantly above baseline (1250.0 MB downloaded)",
    "Abnormally high data egress / upload volume (350.0 MB uploaded)",
    "Geographic location deviation",
    "Device hardware deviation"
  ]
}
```

### 4. `alerts`
```json
{
  "alert_id": "ALT-4EDBDE",
  "user_id": "EMP-1013",
  "timestamp": "2026-09-18T03:15:00Z",
  "event_type": "ANOMALOUS_BEHAVIOR_DETECTED",
  "risk_score": 92.5,
  "severity": "Critical",
  "status": "Open",
  "reasons": ["Multiple failed login attempts detected", "Download volume significantly above baseline"]
}
```

---

## Machine Learning & Feature Engineering Methodology

### Engineered Behavioral Features
1. **`after_hours_ratio`**: Ratio of user actions executed outside standard business hours (7:00 PM – 6:00 AM).
2. **`failed_login_count`**: Cumulative invalid authentication attempts.
3. **`file_access_count`**: Total volume of confidential/system files accessed.
4. **`download_volume_mb`**: Aggregate megabytes downloaded during monitoring window.
5. **`upload_volume_mb`**: Aggregate megabytes uploaded to external endpoints.
6. **`location_deviation_count`**: Logins originating outside approved baseline geography.
7. **`device_deviation_count`**: Logins originating from unregistered MAC addresses.

### Isolation Forest Anomaly Detection
Features are scaled via `StandardScaler` and passed to scikit-learn's `IsolationForest(n_estimators=100, contamination=0.1)`. The tree structure isolates anomalies close to the root, yielding decision scores in $[-0.5, 0.5]$.

### Interpretable Risk Scoring Formula
The decision score is transformed to a $0–100$ scale:
$$\text{Risk Score} = \min\left(100, \text{Normalizer}(\text{Raw Score}) + \sum \text{Rule Additions}\right)$$

- **Risk Categories**:
  - `Low`: 0.0 – 29.9
  - `Medium`: 30.0 – 59.9
  - `High`: 60.0 – 84.9
  - `Critical`: 85.0 – 100.0

---

## REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Admin authentication (`admin` / `Admin@12345`) |
| `GET` | `/api/v1/users` | List monitored users with search & risk filters |
| `GET` | `/api/v1/users/<id>` | Get individual user profile |
| `GET` | `/api/v1/users/<id>/risk-profile` | Get user risk history, timeline, and explanations |
| `GET` | `/api/v1/activities` | List activity logs with pagination and filters |
| `POST` | `/api/v1/activities/synthetic/generate` | Trigger synthetic user behavior generator |
| `POST` | `/api/v1/ml/run-detection` | Run Isolation Forest anomaly detection & update risk scores |
| `GET` | `/api/v1/ml/model-info` | Get model hyperparameters and feature list |
| `GET` | `/api/v1/risk/summary` | Organizational risk summary and category distribution |
| `GET` | `/api/v1/alerts` | List security alerts filtered by status and severity |
| `PATCH` | `/api/v1/alerts/<id>` | Update alert ticket status (`Open`, `Investigating`, `Resolved`) |
| `GET` | `/api/v1/system/status` | System diagnostics and database connection info |

---

## Quickstart & Execution Guide

### Option A: Run with Docker Compose (Recommended)

Run the entire system (MongoDB, Flask Backend, and Angular Frontend) with a single command:

```bash
# Build and start all services in the background
docker compose up -d

# Check status of running containers
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

- **Frontend SOC Dashboard**: [http://localhost:4200](http://localhost:4200)
- **Backend REST API**: [http://localhost:5001](http://localhost:5001)
- **MongoDB**: `localhost:27017`
- **Default Admin Credentials**:
  - **Username**: `admin`
  - **Password**: `Admin@12345`

---

### Option B: Local Manual Setup (Without Docker)

#### Prerequisites
- **Python 3.10+**
- **Node.js v20+** & **npm**
- *(Optional)* Local MongoDB Server (defaults to auto-fallback in-memory store)

### 1. Backend Setup & Launch
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start Flask REST API Server
python run.py
```
*Backend API will run on `http://localhost:5000`.*

### 2. Frontend Setup & Launch
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies (if not already installed)
npm install

# Start Angular development server
npm start
```
*Frontend application will run on `http://localhost:4200`.*

---

## Automated Testing Instructions

To execute the backend pytest test suite covering authentication, feature extraction, ML Isolation Forest scoring, risk heuristics, and REST APIs:

```bash
cd backend
PYTHONPATH=. venv/bin/pytest tests/
```

---

## Limitations & Future Enhancements

### Prototype Limitations
- Demonstrates behavioral anomaly detection using synthetic datasets.
- Single-node Isolation Forest model fit per execution cycle.

### Future Enhancements
- Integration with live Windows Event Logs (EVTX) or Syslog streams.
- Sequential deep learning models (LSTM / Autoencoders) for temporal anomaly sequence modeling.
- Role-Based Access Control (RBAC) multi-analyst workflows.
