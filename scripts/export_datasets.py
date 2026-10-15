"""
Exports the synthetic dataset used by the project to CSV files in datasets/.

Runs the real application pipeline (synthetic generator -> feature engineering ->
Isolation Forest -> risk scoring -> alerts) against an in-memory database, so it never
touches a running MongoDB. Output is deterministic: the random seed, the reference
date and generated IDs are fixed, so re-running produces identical files.

Usage (from the repository root):
    python scripts/export_datasets.py [--days 7] [--seed 2026] [--out datasets]
"""
import argparse
import csv
import os
import random
import sys
import tempfile
import uuid
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

# Configure the backend before it is imported: in-memory DB, throwaway model directory
os.environ['USE_MOCK_DB'] = 'true'
os.environ['APP_ENV'] = 'testing'
os.environ['MODEL_DIR'] = tempfile.mkdtemp(prefix='itd-export-')

import logging  # noqa: E402
logging.disable(logging.INFO)

from app.ml import synthetic_generator  # noqa: E402
from app.services import risk_service  # noqa: E402
from app.utils.db import get_db  # noqa: E402

FEATURES = ['after_hours_ratio', 'failed_login_count', 'file_access_count', 'download_volume_mb',
            'upload_volume_mb', 'location_deviation_count', 'device_deviation_count']


def make_deterministic(seed, reference_date):
    """Pins every source of randomness/time the pipeline uses."""
    random.seed(seed)
    id_rng = random.Random(seed + 1)
    synthetic_generator.utc_now = lambda: reference_date
    risk_service.utc_now_iso = lambda: reference_date.replace(tzinfo=None).isoformat() + 'Z'
    deterministic_uuid4 = lambda: uuid.UUID(int=id_rng.getrandbits(128), version=4)  # noqa: E731
    synthetic_generator.uuid.uuid4 = deterministic_uuid4
    risk_service.uuid.uuid4 = deterministic_uuid4


def write_csv(path, rows, columns):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {os.path.relpath(path, ROOT)}: {len(rows)} rows")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--days', type=int, default=7, help='days of activity to simulate (default 7)')
    parser.add_argument('--seed', type=int, default=2026, help='random seed (default 2026)')
    parser.add_argument('--out', default=os.path.join(ROOT, 'datasets'), help='output directory')
    args = parser.parse_args()

    make_deterministic(args.seed, datetime(2026, 1, 15, tzinfo=timezone.utc))
    synthetic_generator.generate_synthetic_dataset(num_days=args.days, reset_db=True)
    risk_service.run_ml_detection_pipeline()

    db = get_db()
    os.makedirs(args.out, exist_ok=True)
    print(f"Exporting synthetic dataset ({args.days} days, seed {args.seed}):")

    users = list(db.users.find({}, {'_id': 0}).sort('user_id', 1))
    for u in users:
        u['created_at'] = u['created_at'].isoformat()
    write_csv(os.path.join(args.out, 'users.csv'), users,
              ['user_id', 'name', 'email', 'department', 'role', 'baseline_location', 'baseline_device', 'created_at'])

    activities = list(db.activities.find({}, {'_id': 0}).sort([('timestamp', 1), ('activity_id', 1)]))
    for a in activities:
        fd = a.pop('file_details', {}) or {}
        a['filename'] = fd.get('filename', '')
        a['files_accessed_count'] = fd.get('files_accessed_count', 0)
        a['download_size_mb'] = fd.get('download_size_mb', 0.0)
        a['upload_size_mb'] = fd.get('upload_size_mb', 0.0)
    write_csv(os.path.join(args.out, 'activity_logs.csv'), activities,
              ['activity_id', 'user_id', 'timestamp', 'event_type', 'location_ip', 'location_name', 'device_id',
               'app_used', 'filename', 'files_accessed_count', 'download_size_mb', 'upload_size_mb',
               'after_hours', 'failed_logins'])

    scores = list(db.risk_scores.find({}, {'_id': 0}).sort('normalized_risk_score', -1))
    for s in scores:
        metrics = s.pop('feature_metrics')
        for f in FEATURES:
            s[f] = round(metrics[f], 4) if isinstance(metrics[f], float) else metrics[f]
        s['contributing_reasons'] = ' | '.join(s['contributing_reasons'])
    write_csv(os.path.join(args.out, 'risk_scores.csv'), scores,
              ['user_id', 'normalized_risk_score', 'risk_category', 'raw_anomaly_score'] + FEATURES +
              ['contributing_reasons', 'evaluated_at'])

    alerts = list(db.alerts.find({}, {'_id': 0}).sort('risk_score', -1))
    for a in alerts:
        a['reasons'] = ' | '.join(a['reasons'])
    write_csv(os.path.join(args.out, 'alerts.csv'), alerts,
              ['alert_id', 'user_id', 'timestamp', 'event_type', 'risk_score', 'severity', 'status', 'reasons'])


if __name__ == '__main__':
    main()
