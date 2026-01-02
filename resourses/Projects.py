import io
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from extensions import db
from models.Projects import ProjectsModel
from resourses.LoginRequired import login_required


ns = Namespace("projects", description="Operações relacionadas a projetos")

upload_parser = ns.parser()
upload_parser.add_argument(
    "file",
    type="file",
    location="files",
    required=True
)

projects_model = ns.model("Projects", {
    "id": fields.Integer(readonly=True, description="ID do evento"),
    "title": fields.String(required=True, description="Título do evento"),
    "description": fields.String(description="Descrição do evento"),
    "is_draft": fields.Boolean(description="Indica se o evento está em rascunho"),
    "created_at": fields.DateTime(readonly=True, description="Data de criação do evento")
})

@ns.route("/published")
class ProjectsPublished(Resource):
    def get(self):
        return [
            projects.json() for projects in ProjectsModel.query.filter_by(is_draft=False, active=True).all()
        ]
    
@ns.route("/deactivated")
class ProjectsDeactivated(Resource):
    @login_required
    def get(self):
        return [
            projects.json() for projects in ProjectsModel.query.filter_by(active=False).all()
        ]
    
@ns.route("/")
class Projects(Resource):
    def get(self):
        return [
            projects.json() for projects in ProjectsModel.query.filter_by(active=True).all()
        ]
    
    @login_required
    @ns.expect(projects_model)
    def post(self):
        data = request.get_json()
        print(data)
        new_projects = ProjectsModel(
            title=data["title"],
            description=data["description"],
            is_draft=data.get("is_draft", True),
            active=True
        )
        db.session.add(new_projects)
        db.session.commit()
        return new_projects.json(), 201
    
@ns.route("/<int:id>")
class Project(Resource):
    def get(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")
        return projects.json()
    
    @login_required
    @ns.expect(projects_model)
    def put(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")
        
        data = request.get_json()
        projects.title = data["title"]
        projects.description = data["description"]
        projects.is_draft = data.get("is_draft", projects.is_draft)
        projects.active = data.get("active", projects.active)

        db.session.commit()
        return projects.json()
    
    @login_required
    def delete(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")
        
        db.session.delete(projects)
        db.session.commit()
        return {"message": "Evento deletada com sucesso"}, 200
    
@ns.route("/publish/<int:id>")
class ProjectsPublish(Resource):
    @login_required
    def post(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")
        
        projects.is_draft = False
        db.session.commit()
        return {"message": "Evento publicada com sucesso"}, 200
    
@ns.route("/deactivate/<int:id>")
class ProjectsDeactivate(Resource):
    @login_required
    def post(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")

        projects.active = False
        db.session.commit()
        return {"messagem": "Evento desativada com sucesso"}, 200
    
@ns.route("/activate/<int:id>")
class ProjectsActivate(Resource):
    @login_required
    def post(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")

        projects.active = True
        projects.is_draft = True
        db.session.commit()
        return {"message": "Evento ativada com sucesso"}, 200
    
@ns.route("/<int:id>/upload")
class projectsFileUpload(Resource):
    @login_required
    @ns.expect(upload_parser)
    def post(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Projeto não encontrado")

        file = request.files["file"]

        file_bytes = file.read()
        projects.file = file_bytes

        db.session.commit()

        return {"message": "Arquivo enviado com sucesso"}, 200
    
@ns.route("/<int:id>/file")
class projectsFile(Resource):
    def get(self, id):
        projects = ProjectsModel.query.get_or_404(id)
        if not projects:
            ns.abort(404, "Curso não encontrado")
            

        return send_file(
            io.BytesIO(projects.file),
            mimetype="image/png",  # ou image/jpeg dependendo do tipo
            as_attachment=False,
            download_name=f"text_{id}.png"
        )