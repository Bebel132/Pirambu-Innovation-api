from flask import Flask, make_response
from flask_migrate import Migrate
from flask_restx import Api, Resource
from flask_cors import CORS
from dotenv import load_dotenv
import os
from extensions import db
from resourses.Auth import ns as ns_auth
from resourses.Users import ns as ns_users

load_dotenv()

def get_env():
    return os.getenv("ENV", "development").lower()

def is_dev():
    return get_env() == "development"

def is_homolog():
    return get_env() == "homologation"

def is_prod():
    return get_env() == "production"

app = Flask(__name__)

if is_dev() == False:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"sslmode": "require"}
    }
    
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config['REDIRECT_URI'] = os.getenv("REDIRECT_URI")

# URL para onde vai redirecionar após o callback
app.config['FRONTEND_POST_LOGIN_URL'] = os.getenv("FRONTEND_POST_LOGIN_URL", "/")


app.config["SESSION_COOKIE_HTTPONLY"] = True
if is_prod():
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True

elif is_homolog():
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True

else:  # dev local
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

# Swagger – esquema simbólico por cookie, para documentar rotas protegidas
authorizations = {
    "sessionCookie": {
        "type": "apiKey",
        "in": "cookie",
        "name": "session",
        "description": "Autenticação via cookie de sessão após login com Google (/auth/login)."
    }
}

# CORS(app, supports_credentials=True)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": "https://pirambuweb-testes.netlify.app"}},
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Set-Cookie"]
)

api = Api(
    app,
    version="1.0",
    title="Pirambu Innovation API",
    description="API com login via Google OAuth (sessão). Use /auth/login para autenticar.",
    authorizations=authorizations,
    security=None,
    doc="/"  # Swagger UI em "/"
)

db.init_app(app)

migrate = Migrate(app, db)


@api.route('/teste')
class HelloWorld(Resource):
    def get(self):
        html = """<!doctype html>
<html lang="pt-br">
<head><meta charset="utf-8"><title>Hello</title></head>
<body>
    <h1>Hello, world!</h1>
    <p>Deploy OK ✅</p>
</body>
</html>"""
        resp = make_response(html, 200)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        return resp

api.add_namespace(ns_auth)
api.add_namespace(ns_users)

@app.route("/init-db")
def init_db():
    db.create_all()
    return "Banco criado!"

if __name__ == '__main__':
    # Com SQLAlchemy, opcionalmente crie as tabelas no primeiro run:
    with app.app_context():
        db.create_all()
    app.run(debug=True)