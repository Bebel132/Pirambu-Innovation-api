from urllib.parse import urlencode
from flask import jsonify, make_response, redirect, request, session, current_app
from flask_restx import Namespace, Resource, fields
from extensions import db
import requests
from models.AllowedUsers import AllowedUsersModel
from models.User import UserModel
import secrets

from resourses.LoginRequired import login_required

ns = Namespace(
    "auth",
    description=(
        "Autenticação via Google OAuth.\n\n"
        "👉 **[Clique aqui para fazer login com Google](/auth/login)** a sessão será definida e você poderá testar `/auth/profile`.\n\n"
        "👉 **[Clique aqui para fazer login com a Microsoft](/auth/microsoft/login)** a sessão será definida e você poderá testar `/auth/profile`."
    ),
)

# Modelos para Swagger
user_model = ns.model("User", {
    "id": fields.Integer(required=True, description="Id do usuário"),
    "google_id": fields.String(required=False, description="Id do Google (sub)"),
    "username": fields.String(required=False, description="Nome de usuário"),
    "email": fields.String(required=True, description="E-mail"),
})

@ns.route("/login")
class Login(Resource):
    @ns.response(302, "Redireciona para Google")
    def get(self):
        google_auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"

        # Proteção CSRF com 'state'
        state = secrets.token_urlsafe(32)
        session["google_oauth_state"] = state   

        params = {
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "redirect_uri": current_app.config["REDIRECT_URI"],
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",   # se quiser refresh_token (opcional)
            "prompt": "consent",        # garante novo consent (opcional)
            "state": state,
        }
        return redirect(f"{google_auth_endpoint}?{urlencode(params)}")


@ns.route("/callback")
class Callback(Resource):
    @ns.response(302, "Redireciona para FRONTEND_POST_LOGIN_URL")
    @ns.response(400, "Erro no fluxo OAuth")
    def get(self):
        code = request.args.get("code")
        state = request.args.get("state")
        if not code:
            return {"error": "No code provided"}, 400

        # Valida 'state' (CSRF)
        if state != session.get("google_oauth_state"):
            return {"error": "Invalid state"}, 400
        session.pop("google_oauth_state", None)

        # 1) Troca code por token
        token_endpoint = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
            "redirect_uri": current_app.config["REDIRECT_URI"],
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_endpoint, data=data)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return {"error": "Failed to get access token", "details": token_json}, 400

        # 2) Busca dados do usuário
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_response = requests.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        if(AllowedUsersModel.query.filter_by(email=userinfo.get("email")).first() != None):
            # Campos típicos do OpenID
            google_id = userinfo.get("sub")
            email = (userinfo.get("email") or "").strip().lower()
            picture = userinfo.get("picture")
            username = userinfo.get("name")

            if not email:
                return {"error": "Email not provided by Google"}, 400

            # 3) Cria/atualiza usuário (sem senha)
            user = None
            if google_id:
                user = UserModel.query.filter_by(google_id=google_id).first()

            if not user:
                user = UserModel.query.filter_by(email=email).first()

            if not user:
                user = UserModel(
                    google_id=google_id,
                    username=username,
                    email=email,
                    picture=picture,
                )
                db.session.add(user)
            else:
                user.google_id = user.google_id or google_id
                user.username = username or user.username
                user.picture = picture or user.picture

            db.session.commit()

            # 4) Salva na sessão
            session["user_id"] = user.id

            # 5) Redireciona para o front (ou para "/")
            return redirect(current_app.config["FRONTEND_POST_LOGIN_URL"])
        else:
            error_url = f"{current_app.config['FRONTEND_POST_LOGIN_URL']}?error=unauthorized"
            return redirect(error_url)

@ns.route("/microsoft/login")
class MicrosoftLogin(Resource):
    @ns.response(302, "Redireciona para Microsoft")
    def get(self):
        microsoft_auth_endpoint = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        )

        # Proteção CSRF
        state = secrets.token_urlsafe(32)
        session["microsoft_oauth_state"] = state

        params = {
            "client_id": current_app.config["MICROSOFT_CLIENT_ID"],
            "response_type": "code",
            "redirect_uri": current_app.config["MICROSOFT_REDIRECT_URI"],
            "response_mode": "query",
            "scope": "openid profile email User.Read",
            "state": state,
        }

        return redirect(f"{microsoft_auth_endpoint}?{urlencode(params)}")


@ns.route("/microsoft/callback")
class MicrosoftCallback(Resource):
    @ns.response(302, "Redireciona para FRONTEND_POST_LOGIN_URL")
    @ns.response(400, "Erro no fluxo OAuth Microsoft")
    def get(self):
        code = request.args.get("code")
        state = request.args.get("state")

        if not code:
            return {"error": "No code provided"}, 400

        # Valida CSRF
        if request.args.get("state") != session.get("microsoft_oauth_state"):
            return {"error": "Invalid state"}, 400

        session.pop("microsoft_oauth_state", None)

        # 1) Troca code por token
        token_endpoint = (
            "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        )

        data = {
            "client_id": current_app.config["MICROSOFT_CLIENT_ID"],
            "client_secret": current_app.config["MICROSOFT_CLIENT_SECRET"],
            "code": code,
            "redirect_uri": current_app.config["MICROSOFT_REDIRECT_URI"],
            "grant_type": "authorization_code",
            "scope": "openid profile email User.Read",
        }

        token_response = requests.post(token_endpoint, data=data)
        token_response.raise_for_status()
        token_json = token_response.json()

        access_token = token_json.get("access_token")
        if not access_token:
            return {"error": "Failed to get access token"}, 400

        # 2) Busca dados do usuário (Microsoft Graph)
        userinfo_response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_response.raise_for_status()
        ms_user = userinfo_response.json()

        microsoft_id = ms_user.get("id")
        email = (
            ms_user.get("mail")
            or ms_user.get("userPrincipalName")
            or ""
        ).strip().lower()
        username = ms_user.get("displayName")

        if not email:
            return {"error": "Email not provided by Microsoft"}, 400

        # 3) Verifica se usuário é permitido
        if not AllowedUsersModel.query.filter_by(email=email).first():
            error_url = (
                f"{current_app.config['FRONTEND_POST_LOGIN_URL']}"
                "?error=unauthorized"
            )
            return redirect(error_url)

        # 4) Cria ou atualiza usuário
        user = UserModel.query.filter_by(email=email).first()

        if not user:
            user = UserModel(
                email=email,
                username=username,
                # se quiser:
                # microsoft_id=microsoft_id
            )
            db.session.add(user)
        else:
            user.username = username or user.username
            # user.microsoft_id = user.microsoft_id or microsoft_id

        db.session.commit()

        # 5) Salva sessão
        session["user_id"] = user.id

        # 6) Redireciona para frontend
        return redirect(current_app.config["FRONTEND_POST_LOGIN_URL"])


@ns.route("/logout")
class Logout(Resource):
    @login_required
    @ns.doc(security=[{"sessionCookie": []}])
    @ns.response(200, "Logout OK")
    def post(self):
        session.clear()
        resp = make_response({"message": "Logged out"})
        resp.set_cookie(
            "session",
            "",
            expires=0,
            path="/",
            samesite="None",
        )
        return resp


@ns.route("/profile")
class Profile(Resource):
    @login_required
    @ns.response(200, "OK", user_model)
    @ns.response(401, "Não autenticado")
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Not logged in"}, 401

        user = UserModel.query.get(user_id)
        if not user:
            session.pop("user_id", None)
            return {"error": "Usuário não encontrado."}, 401

        return user.json(), 200