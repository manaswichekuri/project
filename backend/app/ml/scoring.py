from app.config.settings import Config


def compute_risk(features, raw_score):
    """
    Combines the Isolation Forest output with transparent heuristic rules.

    `features` is one user's engineered feature row (dict-like); `raw_score` is the model's
    score_samples() value for that user. Returns (risk_score 0-100, risk_category).
    """
    # score_samples returns -s, where s in (0, 1] is the Isolation Forest anomaly score:
    # s <= 0.5 means no distinct anomaly, s -> 1 means clearly anomalous. Map s in [0.5, 1] to 0-50 points.
    anomaly_score = -raw_score
    ml_anomaly_weight = max(0.0, min(50.0, (anomaly_score - 0.5) * 100.0))

    # Heuristic Risk Rule Additions
    rule_points = 0.0
    if features['after_hours_ratio'] > 0.20:
        rule_points += 25.0 * (features['after_hours_ratio'] * 1.5)
    if features['failed_login_count'] >= 3:
        rule_points += min(30.0, features['failed_login_count'] * 7.5)
    if features['download_volume_mb'] > 300.0:
        rule_points += min(35.0, (features['download_volume_mb'] / 500.0) * 20.0)
    if features['upload_volume_mb'] > 100.0:
        rule_points += min(30.0, (features['upload_volume_mb'] / 200.0) * 20.0)
    if features['location_deviation_count'] >= 1:
        rule_points += 25.0 * features['location_deviation_count']
    if features['device_deviation_count'] >= 1:
        rule_points += 20.0 * features['device_deviation_count']

    total_risk_score = round(max(0.0, min(100.0, ml_anomaly_weight + rule_points)), 1)
    return total_risk_score, categorize_risk(total_risk_score)


def categorize_risk(score):
    if score >= Config.RISK_THRESHOLD_CRITICAL:
        return 'Critical'
    if score >= Config.RISK_THRESHOLD_HIGH:
        return 'High'
    if score >= 30.0:
        return 'Medium'
    return 'Low'
