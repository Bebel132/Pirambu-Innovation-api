import io
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from extensions import db
from models.Events import EventsModel
from resourses.LoginRequired import login_required


ns = Namespace("events", description="Operações relacionadas a eventos")

upload_parser = ns.parser()
upload_parser.add_argument(
    "file",
    type="file",
    location="files",
    required=True
)

events_model = ns.model("Events", {
    "id": fields.Integer(readonly=True, description="ID do evento"),
    "title": fields.String(required=True, description="Título do evento"),
    "description": fields.String(description="Descrição do evento"),
    "is_draft": fields.Boolean(description="Indica se o evento está em rascunho"),
    "created_at": fields.DateTime(readonly=True, description="Data de criação do evento")
})

@ns.route("/published")
class EventsPublished(Resource):
    def get(self):
        return [
            events.json() for events in EventsModel.query.filter_by(is_draft=False, active=True).all()
        ]
    
@ns.route("/deactivated")
class EventsDeactivated(Resource):
    @login_required
    def get(self):
        return [
            events.json() for events in EventsModel.query.filter_by(active=False).all()
        ]
    
@ns.route("/")
class Events(Resource):
    def get(self):
        return [
            events.json() for events in EventsModel.query.filter_by(active=True).all()
        ]
    
    @login_required
    @ns.expect(events_model)
    def post(self):
        data = request.get_json()
        print(data)
        new_events = EventsModel(
            title=data["title"],
            description=data["description"],
            is_draft=data.get("is_draft", True),
            active=True
        )
        db.session.add(new_events)
        db.session.commit()
        return new_events.json(), 201
    
@ns.route("/<int:id>")
class Event(Resource):
    def get(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")
        return events.json()
    
    @login_required
    @ns.expect(events_model)
    def put(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")
        
        data = request.get_json()
        events.title = data["title"]
        events.description = data["description"]
        events.is_draft = data.get("is_draft", events.is_draft)
        events.active = data.get("active", events.active)

        db.session.commit()
        return events.json()
    
    @login_required
    def delete(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")
        
        db.session.delete(events)
        db.session.commit()
        return {"message": "Evento deletada com sucesso"}, 200
    
@ns.route("/publish/<int:id>")
class EventsPublish(Resource):
    @login_required
    def post(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")
        
        events.is_draft = False
        db.session.commit()
        return {"message": "Evento publicada com sucesso"}, 200
    
@ns.route("/deactivate/<int:id>")
class EventsDeactivate(Resource):
    @login_required
    def post(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")

        events.active = False
        db.session.commit()
        return {"messagem": "Evento desativada com sucesso"}, 200
    
@ns.route("/activate/<int:id>")
class EventsActivate(Resource):
    @login_required
    def post(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")

        events.active = True
        db.session.commit()
        return {"message": "Evento ativada com sucesso"}, 200
    
@ns.route("/<int:id>/upload")
class eventsFileUpload(Resource):
    @login_required
    @ns.expect(upload_parser)
    def post(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Evento não encontrado")

        file = request.files["file"]

        file_bytes = file.read()
        events.file = file_bytes

        db.session.commit()

        return {"message": "Arquivo enviado com sucesso"}, 200
    
@ns.route("/<int:id>/file")
class eventsFile(Resource):
    def get(self, id):
        events = EventsModel.query.get_or_404(id)
        if not events:
            ns.abort(404, "Curso não encontrado")
            

        return send_file(
            io.BytesIO(events.file),
            mimetype="image/png",  # ou image/jpeg dependendo do tipo
            as_attachment=False,
            download_name=f"text_{id}.png"
        )