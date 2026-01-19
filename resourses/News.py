import io
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from extensions import db
from models.News import NewsModel
from resourses.LoginRequired import login_required


ns = Namespace("news", description="Operações relacionadas a notícias")

upload_parser = ns.parser()
upload_parser.add_argument(
    "file",
    type="file",
    location="files",
    required=True
)

news_model = ns.model("News", {
    "id": fields.Integer(readonly=True, description="ID da notícia"),
    "title": fields.String(required=True, description="Título da notícia"),
    "description": fields.String(description="Descrição da notícia"),
    "is_draft": fields.Boolean(description="Indica se a notícia está em rascunho"),
    "created_at": fields.DateTime(readonly=True, description="Data de criação da notícia")
})

@ns.route("/published")
class NewsPublished(Resource):
    def get(self):
        return [
            news.json() for news in NewsModel.query.filter_by(is_draft=False, active=True).all()
        ]
    
@ns.route("/deactivated")
class NewsDeactivated(Resource):
    @login_required
    def get(self):
        return [
            news.json() for news in NewsModel.query.filter_by(active=False).all()
        ]
    
@ns.route("/")
class News(Resource):
    def get(self):
        return [
            news.json() for news in NewsModel.query.filter_by(active=True).all()
        ]
    
    @login_required
    @ns.expect(news_model)
    def post(self):
        data = request.get_json()
        print(data)
        new_news = NewsModel(
            title=data["title"],
            description=data["description"],
            is_draft=data.get("is_draft", True),
            active=True
        )
        db.session.add(new_news)
        db.session.commit()
        return new_news.json(), 201
    
    @login_required
    def delete(self):
        news = NewsModel.query.filter_by(active=False).all()
        for new in news:
            db.session.delete(new)
        db.session.commit()
        return {"message": "Cursos deletados deletados com sucesso"}, 200
    
@ns.route("/<int:id>")
class New(Resource):
    def get(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")
        return news.json()
    
    @login_required
    @ns.expect(news_model)
    def put(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")
        
        data = request.get_json()
        news.title = data["title"]
        news.description = data["description"]
        news.is_draft = data.get("is_draft", news.is_draft)
        news.active = data.get("active", news.active)

        db.session.commit()
        return news.json()
    
    @login_required
    def delete(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")
        
        db.session.delete(news)
        db.session.commit()
        return {"message": "Notícia deletada com sucesso"}, 200
    
@ns.route("/publish/<int:id>")
class NewsPublish(Resource):
    @login_required
    def post(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")
        
        news.is_draft = False
        db.session.commit()
        return {"message": "Notícia publicada com sucesso"}, 200
    
@ns.route("/deactivate/<int:id>")
class NewsDeactivate(Resource):
    @login_required
    def post(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")

        news.active = False
        db.session.commit()
        return {"messagem": "Notícia desativada com sucesso"}, 200
    
@ns.route("/activate/<int:id>")
class NewsActivate(Resource):
    @login_required
    def post(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")

        news.active = True
        news.is_draft = True
        db.session.commit()
        return {"message": "Notícia ativada com sucesso"}, 200
    
@ns.route("/<int:id>/upload")
class newsFileUpload(Resource):
    @login_required
    @ns.expect(upload_parser)
    def post(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Notícia não encontrada")

        file = request.files["file"]

        file_bytes = file.read()
        news.file = file_bytes

        db.session.commit()

        return {"message": "Arquivo enviado com sucesso"}, 200
    
@ns.route("/<int:id>/file")
class newsFile(Resource):
    def get(self, id):
        news = NewsModel.query.get_or_404(id)
        if not news:
            ns.abort(404, "Curso não encontrado")
            

        return send_file(
            io.BytesIO(news.file),
            mimetype="image/png",  # ou image/jpeg dependendo do tipo
            as_attachment=False,
            download_name=f"text_{id}.png"
        )