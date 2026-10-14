from app.utils.db import get_db

def get_activities(user_id=None, event_type=None, after_hours_only=False, page=1, limit=50):
    db = get_db()
    query = {}

    if user_id:
        query['user_id'] = user_id

    if event_type and event_type != 'All':
        query['event_type'] = event_type

    if after_hours_only:
        query['after_hours'] = True

    total = db.activities.count_documents(query)
    skip = (page - 1) * limit

    activities = list(db.activities.find(query, {'_id': 0}).sort('timestamp', -1).skip(skip).limit(limit))

    return {
        'activities': activities,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit if limit else 1
    }

def add_activity_log(activity_dict):
    db = get_db()
    db.activities.insert_one(activity_dict)
    return activity_dict
