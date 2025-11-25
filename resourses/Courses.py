from datetime import datetime
import io
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from extensions import db
from models.Courses import CourseModel
from resourses.LoginRequired import login_required


ns = Namespace('courses', description='Operações relacionadas a cursos')

upload_parser = ns.parser()
upload_parser.add_argument(
    'file',
    type='file',
    location='files',
    required=True
)

course_model = ns.model('Course', {
    'id': fields.Integer(readonly=True, description='ID do curso'),
    'title': fields.String(required=True, description='Título do curso'),
    'description': fields.String(description='Descrição do curso'),
    'start_date': fields.DateTime(required=True, description='Data de início do curso'),
    'end_date': fields.DateTime(required=True, description='Data de término do curso'),
    'hasFile': fields.Boolean(description='Indica se o curso possui um arquivo associado'),
    'is_draft': fields.Boolean(description='Indica se o curso está em rascunho'),
    'created_at': fields.DateTime(readonly=True, description='Data de criação do curso')
})

@ns.route('/published')
class CoursesPublished(Resource):
    def get(self):
        return [
            course.json() for course in CourseModel.query.filter_by(is_draft=False).all()
        ]

@ns.route('/')
class Courses(Resource):
    @login_required
    def get(self):
        return [
            course.json() for course in CourseModel.query.all()
        ]
    
    @login_required
    @ns.expect(course_model)
    def post(self):
        data = request.get_json()
        new_course = CourseModel(
            title=data['title'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            is_draft=data.get('is_draft', True)
        )
        db.session.add(new_course)
        db.session.commit()
        return new_course.json(), 201
    
@ns.route('/<int:id>')
class Course(Resource):
    @login_required
    @ns.expect(course_model)
    def put(self, id):
        data = request.get_json()
        course = CourseModel.query.get(id)
        if not course:
            ns.abort(404, "Curso não encontrado")
        
        course.title = data['title']
        course.description = data.get('description')
        course.start_date = datetime.fromisoformat(data['start_date'])
        course.end_date = datetime.fromisoformat(data['end_date'])
        course.is_draft = data.get('is_draft', course.is_draft)
        
        db.session.commit()
        return course.json(), 200
    
    @login_required
    def delete(self, id):
        course = CourseModel.query.get(id)
        if not course:
            ns.abort(404, "Curso não encontrado")
        
        db.session.delete(course)
        db.session.commit()
        return {"message": "Curso deletado com sucesso"}, 200
    
@ns.route('/<int:id>/upload')
class CourseFileUpload(Resource):
    @login_required
    @ns.expect(upload_parser)
    def post(self, id):
        course = CourseModel.query.get_or_404(id)

        file = request.files['file']

        file_bytes = file.read()
        course.file = file_bytes

        db.session.commit()
        
        return {"message": "Arquivo enviado com sucesso"}, 200
    
@ns.route('/<int:id>/file')
class CourseFile(Resource):
    def get(self, id):
        course = CourseModel.query.get(id)

        return send_file(
            io.BytesIO(course.file),
            mimetype="image/png",  # ou image/jpeg dependendo do tipo
            as_attachment=False,
            download_name=f"text_{id}.png"
        )