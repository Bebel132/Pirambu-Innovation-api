from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return {"error": "Not logged in"}, 401
        return f(*args, **kwargs)
    return wrapper
