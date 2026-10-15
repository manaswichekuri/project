"""
AI-Powered Insider Threat Detection: standalone ML pipeline.

Runs the same detection pipeline as the web application, without the API, MongoDB or Docker:

  1. Load user activity logs (datasets/*.csv) or generate a fresh synthetic dataset
  2. Engineer 7 behavioral features per user
  3. Fit an unsupervised Isolation Forest anomaly detector
  4. Combine the anomaly score with rule-based risk points into a 0-100 risk score
  5. Explain each score with human-readable reasons

Usage (from the repository root, after `pip install -r backend/requirements.txt`):
    python insider_threat_detection.py                     # analyse datasets/*.csv
    python insider_threat_detection.py --generate --days 14 # analyse freshly generated data
    python insider_threat_detection.py --out results.csv    # also save the results
"""
import argparse
import csv
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'backend'))
os.environ.setdefault('USE_MOCK_DB', 'true')  # only used by --generate
os.environ.setdefault('MODEL_DIR', tempfile.mkdtemp(prefix='itd-standalone-'))

import logging  # noqa: E402
logging.disable(logging.INFO)

from app.config.settings import Config  # noqa: E402
from app.ml.preprocessor import FeaturePreprocessor, FEATURE_COLUMNS  # noqa: E402
from app.ml.model import IsolationForestModel  # noqa: E402
from app.ml.explainer import RiskExplainer  # noqa: E402
from app.ml.scoring import compute_risk  # noqa: E402

DEFAULT_DATA_DIR = os.path.join(ROOT, 'datasets')


def load_csv_dataset(data_dir):
    """Reads users.csv and activity_logs.csv into the structures the pipeline expects."""
    with open(os.path.join(data_dir, 'users.csv'), newline='', encoding='utf-8') as f:
        users = {row['user_id']: row for row in csv.DictReader(f)}

    activities = []
    with open(os.path.join(data_dir, 'activity_logs.csv'), newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            activities.append({
                'user_id': row['user_id'],
                'location_name': row['location_name'],
                'device_id': row['device_id'],
                'after_hours': row['after_hours'].strip().lower() == 'true',
                'failed_logins': int(row['failed_logins']),
                'file_details': {
                    'files_accessed_count': int(row['files_accessed_count']),
                    'download_size_mb': float(row['download_size_mb']),
                    'upload_size_mb': float(row['upload_size_mb']),
                },
            })
    return activities, users


def generate_dataset(days):
    """Generates a fresh synthetic dataset in an in-memory database."""
    from app.ml.synthetic_generator import generate_synthetic_dataset
    from app.utils.db import get_db
    generate_synthetic_dataset(num_days=days, reset_db=True)
    db = get_db()
    activities = list(db.activities.find({}, {'_id': 0}))
    users = {u['user_id']: u for u in db.users.find({}, {'_id': 0})}
    return activities, users


def detect(activities, users, contamination=Config.CONTAMINATION_RATE):
    """Runs feature engineering, Isolation Forest and risk scoring. Returns results sorted by risk."""
    preprocessor = FeaturePreprocessor()
    features = preprocessor.extract_features_from_activities(activities, users)
    X_scaled = preprocessor.fit_transform(features)

    model = IsolationForestModel(contamination=contamination)
    model.train(X_scaled)
    raw_scores = model.predict_anomaly_scores(X_scaled)

    results = []
    for idx, row in features.iterrows():
        score, category = compute_risk(row, float(raw_scores[idx]))
        user = users.get(row['user_id'], {})
        results.append({
            'user_id': row['user_id'],
            'name': user.get('name', ''),
            'department': user.get('department', ''),
            'risk_score': score,
            'risk_category': category,
            'raw_anomaly_score': round(float(raw_scores[idx]), 4),
            **{f: row[f] for f in FEATURE_COLUMNS},
            'reasons': RiskExplainer.generate_reasons_for_user(row.to_dict()),
        })
    results.sort(key=lambda r: (-r['risk_score'], r['raw_anomaly_score']))
    return results


def print_report(results, n_activities):
    print(f"\nAnalysed {n_activities} activity events for {len(results)} users\n")
    print(f"{'Rank':<5}{'User':<10}{'Name':<20}{'Score':>7}  {'Category':<10}Top reason")
    print('-' * 110)
    for i, r in enumerate(results, 1):
        print(f"{i:<5}{r['user_id']:<10}{r['name'][:19]:<20}{r['risk_score']:>7.1f}  {r['risk_category']:<10}{r['reasons'][0]}")

    counts = {c: sum(r['risk_category'] == c for r in results) for c in ('Critical', 'High', 'Medium', 'Low')}
    print('\nRisk distribution: ' + ', '.join(f"{c}: {n}" for c, n in counts.items()))

    flagged = [r for r in results if r['risk_score'] >= Config.RISK_THRESHOLD_HIGH]
    for r in flagged:
        print(f"\n[{r['risk_category'].upper()}] {r['user_id']} {r['name']}: risk {r['risk_score']}")
        for reason in r['reasons']:
            print(f"   - {reason}")


def save_results(results, path):
    columns = ['user_id', 'name', 'department', 'risk_score', 'risk_category', 'raw_anomaly_score'] + FEATURE_COLUMNS + ['reasons']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for r in results:
            writer.writerow({**r, 'reasons': ' | '.join(r['reasons'])})
    print(f"\nSaved results to {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data', default=DEFAULT_DATA_DIR, help='directory with users.csv and activity_logs.csv')
    parser.add_argument('--generate', action='store_true', help='generate a fresh synthetic dataset instead of reading CSVs')
    parser.add_argument('--days', type=int, default=7, help='days of activity to generate with --generate (default 7)')
    parser.add_argument('--out', help='save the results to this CSV file')
    args = parser.parse_args(argv)

    activities, users = generate_dataset(args.days) if args.generate else load_csv_dataset(args.data)
    results = detect(activities, users)
    print_report(results, len(activities))
    if args.out:
        save_results(results, args.out)
    return results


if __name__ == '__main__':
    main()
