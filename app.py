from flask import Flask, make_response
from flask_migrate import Migrate
from flask_restx import Api, Resource
from flask_cors import CORS
from dotenv import load_dotenv
import os
from extensions import db
from resourses.Auth import ns as ns_auth
from resourses.Users import ns as ns_users
from resourses.Courses import ns as ns_courses
from resourses.News import ns as ns_news
from resourses.Events import ns as ns_events
from resourses.Projects import ns as ns_projects
from resourses.Biography import ns as ns_biography

load_dotenv()

app = Flask(__name__)

ENV = os.getenv("ENV", "development").lower()
IS_REMOTE = ENV != "development"

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config['REDIRECT_URI'] = os.getenv("REDIRECT_URI")
app.config['FRONTEND_POST_LOGIN_URL'] = os.getenv("FRONTEND_POST_LOGIN_URL")

app.config["MICROSOFT_CLIENT_ID"] = os.getenv("MICROSOFT_CLIENT_ID")
app.config["MICROSOFT_CLIENT_SECRET"] = os.getenv("MICROSOFT_CLIENT_SECRET")
app.config["MICROSOFT_REDIRECT_URI"] = os.getenv("MICROSOFT_REDIRECT_URI")

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

if IS_REMOTE:
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
else:
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True

CORS(
    app,
    supports_credentials=True,
    #resources={r"/*": {"origins": [
    #    "https://pirambuweb-testes.netlify.app"
    #]}},
    origins=[
        "http://localhost:5500",
        "https://pirambuweb.netlify.app"
    ],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Set-Cookie"]
)

authorizations = {
    "sessionCookie": {
        "type": "apiKey",
        "in": "cookie",
        "name": "session"
    }
}

api = Api(
    app,
    version="1.0",
    title="Pirambu Innovation API",
    description="API com login via Google e Microsoft.",
    authorizations=authorizations,
    security=None,
    doc="/"
)

db.init_app(app)
migrate = Migrate(app, db)

api.add_namespace(ns_auth)
api.add_namespace(ns_users)
api.add_namespace(ns_courses)
api.add_namespace(ns_news)
api.add_namespace(ns_projects)
api.add_namespace(ns_events)
api.add_namespace(ns_biography)

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

@app.route("/init-db")
def init_db():
    db.create_all()
    return "Banco criado!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
