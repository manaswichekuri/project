from pymongo import ReturnDocument
from app.utils.db import get_db
from app.utils.time_utils import utc_now_iso

def get_alerts(status=None, severity=None, user_id=None):
    db = get_db()
    query = {}

    if status and status != 'All':
        query['status'] = status
    if severity and severity != 'All':
        query['severity'] = severity
    if user_id:
        query['user_id'] = user_id

    alerts = list(db.alerts.find(query, {'_id': 0}).sort('timestamp', -1))
    return alerts

def update_alert_status(alert_id, new_status, notes=None):
    db = get_db()
    valid_statuses = ['Open', 'Investigating', 'Resolved']
    if new_status not in valid_statuses:
        return None

    update_fields = {
        'status': new_status,
        'updated_at': utc_now_iso()
    }
    if notes:
        update_fields['admin_notes'] = notes

    result = db.alerts.find_one_and_update(
        {'alert_id': alert_id},
        {'$set': update_fields},
        projection={'_id': 0},
        return_document=ReturnDocument.AFTER
    )
    return result

def get_alert_stats():
    db = get_db()
    total = db.alerts.count_documents({})
    open_count = db.alerts.count_documents({'status': 'Open'})
    investigating_count = db.alerts.count_documents({'status': 'Investigating'})
    resolved_count = db.alerts.count_documents({'status': 'Resolved'})

    critical_count = db.alerts.count_documents({'severity': 'Critical'})
    high_count = db.alerts.count_documents({'severity': 'High'})
    medium_count = db.alerts.count_documents({'severity': 'Medium'})
    low_count = db.alerts.count_documents({'severity': 'Low'})

    return {
        'total': total,
        'status_breakdown': {
            'Open': open_count,
            'Investigating': investigating_count,
            'Resolved': resolved_count
        },
        'severity_breakdown': {
            'Critical': critical_count,
            'High': high_count,
            'Medium': medium_count,
            'Low': low_count
        }
    }
