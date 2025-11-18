from flask import Flask, make_response
from flask_restx import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)

@api.route('/teste')
class hello_world(Resource):
    def get(self):
        html = """
                <!doctype html>
                <html lang="pt-br">
                <head><meta charset="utf-8"><title>Hello</title></head>
                <body>
                    <h1>Hello, world!</h1>
                    <p>Deploy OK ✅</p>
                </body>
                </html>
                """
        resp = make_response(html, 200)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        return resp


if __name__ == '__main__':
    app.run(debug=True)