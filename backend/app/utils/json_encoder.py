import json
from datetime import datetime, date
from bson import ObjectId
from flask import jsonify

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def jsonify_doc(data, status_code=200):
    """Helper to convert dict/list containing ObjectId/datetime to JSON response."""
    encoded = json.loads(json.dumps(data, cls=CustomJSONEncoder))
    return jsonify(encoded), status_code
