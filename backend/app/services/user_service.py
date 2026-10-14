import re
from app.utils.db import get_db

def get_all_users(search_query=None, department=None, risk_category=None):
    db = get_db()
    query = {}

    if search_query:
        search_query = re.escape(search_query.strip()[:100])
        query['$or'] = [
            {'name': {'$regex': search_query, '$options': 'i'}},
            {'user_id': {'$regex': search_query, '$options': 'i'}},
            {'role': {'$regex': search_query, '$options': 'i'}}
        ]

    if department and department != 'All':
        query['department'] = department

    users = list(db.users.find(query, {'_id': 0}))

    # Attach latest risk score to each user
    for user in users:
        latest_risk = db.risk_scores.find_one(
            {'user_id': user['user_id']},
            sort=[('evaluated_at', -1)],
            projection={'_id': 0}
        )
        if latest_risk:
            user['current_risk_score'] = latest_risk.get('normalized_risk_score', 0)
            user['risk_category'] = latest_risk.get('risk_category', 'Low')
            user['last_evaluated_at'] = latest_risk.get('evaluated_at')
            user['reasons'] = latest_risk.get('contributing_reasons', [])
        else:
            user['current_risk_score'] = 0.0
            user['risk_category'] = 'Low'
            user['last_evaluated_at'] = None
            user['reasons'] = []

    if risk_category and risk_category != 'All':
        users = [u for u in users if u['risk_category'].lower() == risk_category.lower()]

    return users

def get_user_by_id(user_id):
    db = get_db()
    user = db.users.find_one({'user_id': user_id}, {'_id': 0})
    if not user:
        return None

    latest_risk = db.risk_scores.find_one(
        {'user_id': user_id},
        sort=[('evaluated_at', -1)],
        projection={'_id': 0}
    )
    if latest_risk:
        user['current_risk_score'] = latest_risk.get('normalized_risk_score', 0)
        user['risk_category'] = latest_risk.get('risk_category', 'Low')
        user['last_evaluated_at'] = latest_risk.get('evaluated_at')
        user['reasons'] = latest_risk.get('contributing_reasons', [])
    else:
        user['current_risk_score'] = 0.0
        user['risk_category'] = 'Low'
        user['last_evaluated_at'] = None
        user['reasons'] = []

    return user

def get_user_risk_profile(user_id):
    db = get_db()
    user = get_user_by_id(user_id)
    if not user:
        return None

    # Risk score history timeline
    risk_history = list(db.risk_scores.find(
        {'user_id': user_id},
        {'_id': 0}
    ).sort('evaluated_at', 1))

    # Recent activity logs (last 30 events)
    activities = list(db.activities.find(
        {'user_id': user_id},
        {'_id': 0}
    ).sort('timestamp', -1).limit(30))

    # Triggered alerts for this user
    alerts = list(db.alerts.find(
        {'user_id': user_id},
        {'_id': 0}
    ).sort('timestamp', -1))

    return {
        'user': user,
        'risk_history': risk_history,
        'recent_activities': activities,
        'alerts': alerts
    }
