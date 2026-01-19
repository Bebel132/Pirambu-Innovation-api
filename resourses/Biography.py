import io
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from extensions import db
from resourses.LoginRequired import login_required
from models.Biography import BiographyModel

ns = Namespace("biography", description="Operações relacionadas a seção 'sobre nós'")

upload_parser = ns.parser()
upload_parser.add_argument(
    "file",
    type="file",
    location="files",
    required=True
)

biography_model = ns.model("Biography", {
    "description": fields.String(description="Descrição da biografia"),
})

@ns.route("/")
class Biography(Resource):
    def get(self):
        biography = BiographyModel.query.first()
        if biography:
            return biography.json()
        return {}, 404

@ns.route("/edit")
class BiographyEdit(Resource):
    @login_required
    @ns.expect(biography_model)
    def put(self):
        data = ns.payload
        biography = BiographyModel.query.first()
        if not biography:
            biography = BiographyModel(
                description=data.get("description"),
                instagram=data.get("instagram"),
                whatsapp=data.get("whatsapp"),
                endereco=data.get("endereco"),
            )
            db.session.add(biography)
        else:
            biography.description = data.get("description", biography.description)
            biography.instagram = data.get("instagram", biography.instagram)
            biography.whatsapp = data.get("whatsapp", biography.whatsapp)
            biography.endereco = data.get("endereco", biography.endereco)
        db.session.commit()
        return biography.json()

@ns.route("/upload")
class BiographyUpload(Resource):
    @login_required
    @ns.expect(upload_parser)
    def post(self):
        biography = BiographyModel.query.first()
        if not biography:
            biography = BiographyModel()
            db.session.add(biography)

        file = request.files["file"]
        file_bytes = file.read()
        biography.file = file_bytes

        db.session.commit()
        return {"message": "Arquivo enviado com sucesso"}, 200

@ns.route("/file")
class BiographyFile(Resource):
    def get(self):
        biography = BiographyModel.query.first()
        if not biography or not biography.file:
            ns.abort(404, "Arquivo não encontrado")

        return send_file(
            io.BytesIO(biography.file),
            mimetype="image/png",
            as_attachment=False,
            download_name=f"text_{biography.id}.png"
        )