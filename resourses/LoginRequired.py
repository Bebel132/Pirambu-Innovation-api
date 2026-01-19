from functools import wraps
from flask import session, jsonify

from models.User import UserModel


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        # Não está logado
        if not user_id:
            return {"error": "Not logged in"}, 401

        # Usuário não existe mais
        user = UserModel.query.get(user_id)
        if not user:
            session.clear()
            return {"error": "User not found"}, 401

        # Usuário perdeu acesso
        if not user.active:
            session.clear()
            return {"error": "Access revoked"}, 403

        return f(*args, **kwargs)

