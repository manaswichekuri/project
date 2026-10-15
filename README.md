# AI-Powered Insider Threat Detection and Risk Scoring System
### B.Tech CSE Engineering Capstone Project – 1 (23IE4053R/23IE4053A) · KLH University, Hyderabad · A.Y. 2026–2027

| University ID | Team Member |
|---|---|
| 2320030366 | P. Sri Harini |
| 2320030245 | Manaswi Ch |
| 2320030210 | Hruday K |

**Project Guide:** Dr. K Swanthana, Department of CSE

📄 [Abstract](docs/AI_Insider_Threat_Abstract.docx) · 📑 [Research Paper](docs/Research_Paper.docx) · 📊 [Review Presentation](docs/AI_Insider_Threat_Review_Presentation.pptx) · 🗂️ [Datasets](datasets/) · 🐍 [Standalone ML Script](insider_threat_detection.py)

---

## Project Abstract

*AI-Powered Insider Threat Detection and User Behavior Analytics System* ([abstract document](docs/AI_Insider_Threat_Abstract.docx))

Organizations today face increasing cybersecurity threats not only from external attackers but also from insider threats caused by employees, contractors, or compromised user accounts. Since insiders already have authorized access to organizational resources, detecting malicious or abnormal activities is significantly more challenging than preventing external attacks. Traditional security systems primarily rely on predefined rules and signatures, making them less effective in identifying unusual user behavior.

This project proposes an AI-Powered Insider Threat Detection and User Behavior Analytics (UBA) System that continuously monitors user activities and identifies suspicious behavior using machine learning techniques. The system collects user activity logs such as login times, login locations, file access patterns, download frequency, device usage, and other security events. It establishes a baseline of normal behavior for each user and compares ongoing activities against this profile to detect anomalies.

When suspicious behavior is identified, the system assigns a dynamic risk score based on the severity of the detected actions and generates real-time alerts for security administrators. An interactive dashboard provides visual insights into user activities, anomaly trends, risk levels, and incident timelines, enabling administrators to investigate potential insider threats efficiently. Additionally, the system generates AI-assisted summaries that explain detected incidents in simple language and recommend appropriate mitigation measures.

The proposed solution aims to reduce the time required to identify insider threats, improve organizational security, and support proactive incident response. By integrating cybersecurity principles with artificial intelligence and behavioral analytics, this project offers a scalable and practical approach to protecting sensitive organizational data from internal misuse and compromised accounts.

> [!NOTE]
> **Proposal vs. current implementation.** This repository implements per-user behavioral baselines, 7 engineered features, Isolation Forest anomaly detection, 0–100 risk scoring, alerts, plain-language explanations, and the SOC dashboard, all on a **synthetic** dataset. These items from the abstract and research paper are **not yet implemented**: AI-generated incident summaries with mitigation recommendations, the Random Forest / XGBoost comparison models, evaluation on the CMU CERT dataset, and continuous real-time log ingestion (detection currently runs on demand).

---

## Executive Summary & Overview
The **AI-Powered Insider Threat Detection and Risk Scoring System** is an end-to-end web application and Security Operations Center (SOC) dashboard designed to detect suspicious insider activity using machine learning behavioral analysis.

Instead of relying solely on static rules or black-box predictions, this system aggregates fine-grained user activity logs, extracts 7 engineered behavioral features, fits an unsupervised **Isolation Forest** anomaly detection model, normalizes anomaly scores into an interpretable **0–100 risk scale**, and generates **human-readable explainability reasons** for security administrators.

> [!NOTE]
> **Academic Prototype Note**: This system is a working academic prototype designed for local demonstration using synthetic dataset generation. It explicitly separates simulated/demo activity from real enterprise monitoring.

---

## Repository Contents

| What | Where |
|---|---|
| Project documents: abstract, research paper, review presentation (12 slides) | [`docs/`](docs/) |
| Datasets used (synthetic users, activity logs, risk scores, alerts) | [`datasets/`](datasets/) (see [`datasets/README.md`](datasets/README.md)) |
| Standalone ML pipeline (one runnable `.py`, no web app needed) | [`insider_threat_detection.py`](insider_threat_detection.py) |
| Machine learning code | [`backend/app/ml/`](backend/app/ml/): [`synthetic_generator.py`](backend/app/ml/synthetic_generator.py), [`preprocessor.py`](backend/app/ml/preprocessor.py), [`model.py`](backend/app/ml/model.py), [`scoring.py`](backend/app/ml/scoring.py), [`explainer.py`](backend/app/ml/explainer.py) |
| REST API (Flask) | [`backend/app/routes/`](backend/app/routes/), [`backend/app/services/`](backend/app/services/) |
| SOC dashboard (Angular) | [`frontend/src/app/`](frontend/src/app/) |
| Tests | [`backend/tests/`](backend/tests/), `frontend/src/**/*.spec.ts` |
| Dataset export script | [`scripts/export_datasets.py`](scripts/export_datasets.py) |
| Deployment | [`docker-compose.yml`](docker-compose.yml), [`backend/Dockerfile`](backend/Dockerfile), [`frontend/Dockerfile`](frontend/Dockerfile) |

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
project/
│
├── backend/
│   ├── app/
│   │   ├── config/             # Environment & threshold settings
│   │   ├── services/           # Business logic & database operations
│   │   ├── ml/                 # Generator, Preprocessor, Isolation Forest, Scoring, Explainer
│   │   ├── routes/             # REST API endpoints (Auth, Users, Activity, Risk, Alerts)
│   │   └── utils/              # MongoDB connection, JWT auth, request parsing, JSON serializers
│   ├── datasets/               # Trained model artifact (created at runtime, git-ignored)
│   ├── tests/                  # Pytest automated test suites
│   ├── requirements.txt        # Runtime dependencies (requirements-dev.txt adds pytest)
│   ├── Dockerfile              # Gunicorn production image
│   ├── .env.example
│   ├── run.py                  # Development server entry point
│   └── wsgi.py                 # Production WSGI entry point (gunicorn)
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/           # Guards, JWT interceptor, Services (Api, Auth, Notifications)
│   │   │   ├── models/         # TypeScript interfaces
│   │   │   ├── pages/          # Login, Dashboard, Users, User-Detail, Activity-Logs, Alerts, Analytics, System-Info
│   │   │   └── shared/         # Navbar, Sidebar, MetricCard, RiskBadge
│   │   ├── environments/       # API base URL
│   │   └── styles.scss         # Cyber SOC Dark Theme
│   ├── angular.json
│   ├── proxy.conf.json         # Dev-server proxy for /api
│   ├── nginx.conf              # Production web server + API proxy
│   ├── Dockerfile
│   └── package.json
│
├── docs/                       # Abstract, research paper, review presentation
├── datasets/                   # Synthetic datasets used (CSV) + data dictionary
├── scripts/
│   └── export_datasets.py      # Regenerates datasets/ from the real pipeline
├── insider_threat_detection.py # Standalone ML pipeline (no web app / DB needed)
├── docker-compose.yml
├── .env.example
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
Features are scaled via `StandardScaler` and passed to scikit-learn's `IsolationForest(n_estimators=100, contamination=0.1)`. Anomalies are isolated close to the root of the trees. The model's anomaly score $s \in (0, 1]$ (exposed as `-score_samples`) is $\le 0.5$ for ordinary behavior and approaches $1$ for clear outliers.

### Interpretable Risk Scoring Formula
The anomaly score contributes up to 50 points, and transparent heuristic rules (after-hours ratio, failed logins, download/upload volume, location/device deviations) add the rest:
$$\text{ML Points} = \text{clip}\big((s - 0.5) \times 100,\ 0,\ 50\big)$$
$$\text{Risk Score} = \min\left(100,\ \text{ML Points} + \sum \text{Rule Additions}\right)$$

- **Risk Categories**:
  - `Low`: 0.0 – 29.9
  - `Medium`: 30.0 – 59.9
  - `High`: 60.0 – 84.9 (`RISK_THRESHOLD_HIGH`)
  - `Critical`: 85.0 – 100.0 (`RISK_THRESHOLD_CRITICAL`)

---

## REST API Documentation

All endpoints except `/api/v1/health` and `/api/v1/auth/login` require an `Authorization: Bearer <token>` header. Tokens are signed JWTs (HS256, signed with `SECRET_KEY`) that expire after `JWT_EXPIRES_HOURS`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Public liveness probe (used by Docker healthchecks) |
| `POST` | `/api/v1/auth/login` | Admin authentication, returns a JWT (`admin` / `Admin@12345` by default) |
| `GET` | `/api/v1/auth/me` | Current admin profile for the supplied token |
| `GET` | `/api/v1/users` | List monitored users with search & risk filters |
| `GET` | `/api/v1/users/<id>` | Get individual user profile |
| `GET` | `/api/v1/users/<id>/risk-profile` | Get user risk history, timeline, and explanations |
| `GET` | `/api/v1/activities` | List activity logs (`page`, `limit` ≤ 500, `user_id`, `event_type`, `after_hours`) |
| `GET` | `/api/v1/activities/stats` | Activity counts per event type |
| `POST` | `/api/v1/activities` | Ingest one activity log (`user_id`, `event_type`, `timestamp` required) |
| `POST` | `/api/v1/activities/synthetic/generate` | Trigger synthetic user behavior generator (`days` 1–60, `reset`) |
| `POST` | `/api/v1/ml/run-detection` | Run Isolation Forest anomaly detection & update risk scores |
| `GET` | `/api/v1/ml/model-info` | Get model hyperparameters and feature list |
| `GET` | `/api/v1/risk/summary` | Organizational risk summary and category distribution |
| `GET` | `/api/v1/alerts` | List security alerts filtered by status and severity |
| `GET` | `/api/v1/alerts/stats` | Alert counts by status and severity |
| `PATCH` | `/api/v1/alerts/<id>` | Update alert ticket status (`Open`, `Investigating`, `Resolved`) and `notes` |
| `GET` | `/api/v1/system/status` | System diagnostics and database connection info |

---

## Quickstart & Execution Guide

### Option A: Deploy with Docker Compose (Recommended)

The stack runs MongoDB, the Flask API (served by Gunicorn as a non-root user), and the Angular build (served by Nginx). Only the Nginx port is published. Nginx serves the SPA and proxies `/api/` to the backend over the internal Docker network, so MongoDB and the API are not exposed to the host.

#### Prerequisites
- **Docker** with the **Compose v2** plugin (Docker Desktop on macOS/Windows, or Docker Engine on Linux). Check with `docker compose version`.
- **Git** and **Python 3** (Python is only used to generate a secret key).

#### Step 1: Get the code
```bash
git clone https://github.com/manaswichekuri/project.git
cd project
```

#### Step 2: Create your `.env` file
```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Open `.env` and paste the generated value after `SECRET_KEY=`. Docker Compose refuses to start while `SECRET_KEY` is empty. For any server reachable from the internet, also change `ADMIN_PASSWORD`. The `.env` file is git-ignored, so never commit it.

#### Step 3: Build and start
```bash
docker compose up -d --build
docker compose ps
```
The first build takes a few minutes. Wait until all three containers (`insider_threat_mongo`, `insider_threat_backend`, `insider_threat_frontend`) show **(healthy)**.

#### Step 4: Open the dashboard and load demo data
1. Go to **[http://localhost:8080](http://localhost:8080)**. Change the port with `FRONTEND_PORT` in `.env`.
2. Log in with `ADMIN_USERNAME` / `ADMIN_PASSWORD` from `.env` (defaults to `admin` / `Admin@12345`).
3. Click **Generate Data** in the top bar, then **Run Detection**. The dashboard, users, alerts, and analytics pages then fill with results.

The API is available through the same port at `http://localhost:8080/api/v1` (see [REST API Documentation](#rest-api-documentation)).

#### Day-to-day commands
| Task | Command |
|---|---|
| Stop the app (data is kept) | `docker compose down` |
| Start it again | `docker compose up -d` |
| Update after pulling new code | `git pull && docker compose up -d --build` |
| Follow the backend logs | `docker compose logs -f backend` |
| Check container health | `docker compose ps` |
| **Delete all data** and start fresh (cannot be undone) | `docker compose down -v` |

Data lives in two named Docker volumes: `mongodb_data` (database) and `model_data` (trained model). These survive `down` and `up`; only `down -v` removes them.

#### Troubleshooting
- **`Set SECRET_KEY in .env`**: Step 2 was skipped, or `SECRET_KEY=` is still empty.
- **`port is already allocated`**: another program is using port 8080. Set `FRONTEND_PORT=8081` (or another free port) in `.env` and run `docker compose up -d` again.
- **Backend stays `unhealthy`**: run `docker compose logs backend`. In production mode the API stops with a clear error if it cannot reach MongoDB, rather than silently using a temporary in-memory database.
- **Logged out unexpectedly**: sessions expire after `JWT_EXPIRES_HOURS` (default 8). Changing `SECRET_KEY` also signs everyone out.
- **Changed `ADMIN_PASSWORD`**: run `docker compose up -d` so the backend restarts. The stored password is updated on startup.

#### Deploying to a server
Run the same steps on any Linux VM with Docker installed. Put a TLS-terminating reverse proxy (Caddy, Traefik, or a cloud load balancer) in front of `FRONTEND_PORT` to serve HTTPS. If browsers will reach the API from a different domain than the dashboard, add that origin to `CORS_ORIGINS`.

#### Environment variables
| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | *(required)* | JWT signing key |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | `admin` / `Admin@12345` | Seeded admin account (changing the password re-hashes it on restart) |
| `JWT_EXPIRES_HOURS` | `8` | Session lifetime |
| `FRONTEND_PORT` | `8080` | Host port for the dashboard |
| `CORS_ORIGINS` | `http://localhost` | Comma-separated origins allowed for direct API access |
| `GUNICORN_WORKERS` | `2` | API worker processes |
| `CONTAMINATION_RATE`, `RISK_THRESHOLD_HIGH`, `RISK_THRESHOLD_CRITICAL` | `0.1`, `60`, `85` | ML / scoring tuning |

---

### Option B: Local Development (Without Docker)

#### Prerequisites
- **Python 3.10+**
- **Node.js v20+** & **npm**
- *(Optional)* Local MongoDB server. In development the API falls back to an in-memory store when MongoDB is unreachable (`ALLOW_MOCK_FALLBACK=true`).

### 1. Backend Setup & Launch
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # optional: adjust settings
python run.py
```
*Backend API runs on `http://localhost:5001`.*

### 2. Frontend Setup & Launch
```bash
cd frontend
npm ci
npm start
```
*The frontend runs on `http://localhost:4200`. `ng serve` proxies `/api` to `http://localhost:5001` (see `proxy.conf.json`).*

---

### Option C: Run the ML Pipeline Standalone

To see the detection results without the web app, database or Docker, run the single-file pipeline on the bundled datasets:

```bash
pip install -r backend/requirements.txt
python insider_threat_detection.py                       # analyse datasets/*.csv
python insider_threat_detection.py --generate --days 14  # analyse a freshly simulated dataset
python insider_threat_detection.py --out results.csv     # also save the results as CSV
```

It prints every user ranked by risk score, the risk distribution, and the explanation for each flagged user. It uses the same feature engineering, Isolation Forest and scoring code as the web app, so the scores are identical.

---

## Automated Testing Instructions

Backend (pytest, using an isolated in-memory DB per test). It covers JWT auth, input validation, feature extraction, Isolation Forest scoring, risk categorisation, and every REST endpoint:

```bash
cd backend
source venv/bin/activate
pytest -q
```

Frontend (Karma + Jasmine, headless Chrome) and production build:

```bash
cd frontend
npx ng test --watch=false --browsers=ChromeHeadless
npm run build
```

---

## Research Paper & References

The accompanying paper, [*AI-Powered Insider Threat Detection System Using User Behavior Analytics and Machine Learning*](docs/Research_Paper.docx) (Manaswi Chekuri, Sri Harini, Hruday; Dept. of CSE, KLH University), surveys IEEE insider-threat research and sets out the system design, feature engineering, risk scoring, explainability and evaluation methodology. Performance figures quoted in the paper come from the cited studies; they are not results of this project.

**References**
1. A. A. Alzahrani et al., "A Review of Recent Advances, Challenges, and Opportunities in Malicious Insider Threat Detection Using Machine Learning Methods," *IEEE Access*, vol. 12, pp. 30907–30927, 2024. [doi:10.1109/ACCESS.2024.3369906](https://doi.org/10.1109/ACCESS.2024.3369906)
2. "Machine Learning-Based Approaches for Malicious Insider Threat Detection: A Survey of Recent Advances and Open Issues," *ICOIICS*, 2025. [doi:10.1109/ICOIICS67115.2025.11390400](https://doi.org/10.1109/ICOIICS67115.2025.11390400)
3. "Insider Threat Detection Model Using Anomaly-Based Isolation Forest Algorithm," *IEEE Access*, vol. 11, pp. 118170–118185, 2023. [doi:10.1109/ACCESS.2023.3326750](https://doi.org/10.1109/ACCESS.2023.3326750)
4. "Detecting and Preventing Cyber Insider Threats: A Survey," 2018, IEEE Xplore document 8278157.
5. "DTITD: An Intelligent Insider Threat Detection Framework Based on Digital Twin and Self-Attention Based Deep Learning Models," *IEEE Access*, vol. 11, pp. 114013–114030, 2023. [doi:10.1109/ACCESS.2023.3324371](https://doi.org/10.1109/ACCESS.2023.3324371)
6. "Anomaly-Based Insider Threat Detection Using Deep Autoencoders," *IEEE ICDMW*, 2018. [doi:10.1109/ICDMW.2018.00014](https://doi.org/10.1109/ICDMW.2018.00014)
7. "User Behaviour based Insider Threat Detection in Critical Infrastructures," *ICSCCC*, 2021. [doi:10.1109/ICSCCC51823.2021.9478137](https://doi.org/10.1109/ICSCCC51823.2021.9478137)
8. "ITDBERT: Temporal-semantic Representation for Insider Threat Detection," *IEEE ISCC*, 2021. [doi:10.1109/ISCC53001.2021.9631538](https://doi.org/10.1109/ISCC53001.2021.9631538)
9. "A Graph Convolution Neural Network Based Method for Insider Threat Detection," *IEEE ISPA/BDCloud/SocialCom/SustainCom*, 2022. [doi:10.1109/ISPA-BDCloud-SocialCom-SustainCom57177.2022.00016](https://doi.org/10.1109/ISPA-BDCloud-SocialCom-SustainCom57177.2022.00016)
10. "Employee Watcher: A Machine Learning-based Hybrid Insider Threat Detection Framework," *CSNet*, 2023. [doi:10.1109/CSNet59123.2023.10339777](https://doi.org/10.1109/CSNet59123.2023.10339777)
11. "NLP and Neural Networks for Insider Threat Detection," *IEEE TrustCom*, 2024. [doi:10.1109/TrustCom63139.2024.00279](https://doi.org/10.1109/TrustCom63139.2024.00279)

---

## Limitations & Future Enhancements

### Prototype Limitations
- Demonstrates behavioral anomaly detection using synthetic datasets.
- Single-node Isolation Forest model fit per execution cycle.

### Future Enhancements
- Integration with live Windows Event Logs (EVTX) or Syslog streams.
- Sequential deep learning models (LSTM / Autoencoders) for temporal anomaly sequence modeling.
- Role-Based Access Control (RBAC) multi-analyst workflows.
