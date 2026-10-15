# Datasets

All data in this folder is **synthetic**. It was produced by the project's own behavior simulator (`backend/app/ml/synthetic_generator.py`), not collected from real employees. No real people, accounts or organizations are represented. The IP addresses come from the reserved documentation ranges (`198.51.100.0/24`, `203.0.113.0/24`).

The files are a reproducible snapshot of one full pipeline run: 7 simulated days (2026-01-08 to 2026-01-14), random seed `2026`.

| File | Rows | Contents |
|---|---|---|
| [`users.csv`](users.csv) | 14 | Monitored employees and their behavioral baselines |
| [`activity_logs.csv`](activity_logs.csv) | 611 | Raw activity events: logins, logouts, file access/download/upload, app usage |
| [`risk_scores.csv`](risk_scores.csv) | 14 | Engineered features, Isolation Forest output, final risk score, category and reasons per user |
| [`alerts.csv`](alerts.csv) | 4 | Security alerts raised for users at or above the High risk threshold |

## Simulated user profiles

| Profile | Users | Behavior |
|---|---|---|
| Normal | `EMP-1001` – `EMP-1010` | 4–7 events/day during office hours (09:00–17:00), home office location (New York), registered device, small file transfers, no failed logins |
| Occasional anomaly | `EMP-1011`, `EMP-1012` | Mostly normal; about 25% of events are late-evening (20:00–22:00) access to confidential files, with moderate downloads and occasional failed logins |
| Severe anomaly | `EMP-1013` (rogue admin / exfiltration), `EMP-1014` (compromised credentials) | 8–14 events/day; about 45% are 01:00–04:00 events from foreign locations on unregistered devices, with repeated failed logins and very large downloads/uploads of confidential files |

Event mix in `activity_logs.csv`: LOGIN 156, FILE_ACCESS 148, LOGOUT 143, APP_USAGE 122, FILE_DOWNLOAD 27, FILE_UPLOAD 15.

## Column dictionary

**`users.csv`**: `user_id`, `name`, `email`, `department`, `role`, `baseline_location` (usual office), `baseline_device` (registered device ID), `created_at`.

**`activity_logs.csv`**
| Column | Description |
|---|---|
| `activity_id`, `user_id`, `timestamp` (UTC, ISO-8601) | Event identity |
| `event_type` | `LOGIN`, `LOGOUT`, `FILE_ACCESS`, `FILE_DOWNLOAD`, `FILE_UPLOAD`, `APP_USAGE` |
| `location_ip`, `location_name` | Source of the event |
| `device_id` | Device used (`UNREGISTERED-MAC-*` = not the user's registered device) |
| `app_used` | Application involved |
| `filename`, `files_accessed_count`, `download_size_mb`, `upload_size_mb` | File activity in the event |
| `after_hours` | `True` if outside standard working hours |
| `failed_logins` | Failed authentication attempts in the event |

**`risk_scores.csv`**: one row per user with the 7 engineered features used by the model:
| Feature | Meaning (over the whole analysis period) |
|---|---|
| `after_hours_ratio` | Fraction of the user's events outside working hours |
| `failed_login_count` | Total failed login attempts |
| `file_access_count` | Total files accessed |
| `download_volume_mb` / `upload_volume_mb` | Total data downloaded / uploaded |
| `location_deviation_count` | Events from a location other than the baseline |
| `device_deviation_count` | Events from a device other than the baseline |

It also has `raw_anomaly_score` (Isolation Forest `score_samples`; more negative means more anomalous), `normalized_risk_score` (0–100), `risk_category` (`Low` < 30 ≤ `Medium` < 60 ≤ `High` < 85 ≤ `Critical`), `contributing_reasons` (separated by `|`) and `evaluated_at`.

**`alerts.csv`**: `alert_id`, `user_id`, `timestamp`, `event_type`, `risk_score`, `severity`, `status`, `reasons`.

## Regenerating

From the repository root, with the backend dependencies installed (`pip install -r backend/requirements.txt`):

```bash
python scripts/export_datasets.py                      # recreates these exact files
python scripts/export_datasets.py --days 14 --seed 7   # a different simulation
```

The script runs the real application pipeline against an in-memory database, so it never touches a running MongoDB.

To analyse these files without the web app, see [`insider_threat_detection.py`](../insider_threat_detection.py) in the repository root.
