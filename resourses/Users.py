from flask import request
from flask_restx import Namespace, Resource, fields
from models.AllowedUsers import AllowedUsersModel
from models.User import UserModel
from extensions import db


ns = Namespace("users", description=("Operações relacionadas a usuários."))

# Modelos para Swagger
user_model = ns.model("User", {
    "email": fields.String(required=True, description="E-mail"),
})

@ns.route('/')
class Users(Resource):
    @ns.doc(security=[{"sessionCookie": []}])
    def get(self):
        return [
            user.json() for user in UserModel.query.all()
        ]
    
    
@ns.route('/allowedUsers/')
class Users(Resource):
    @ns.doc(security=[{"sessionCookie": []}])
    def get(self):
        return [
            allowedUser.json() for allowedUser in AllowedUsersModel.query.all() 
        ]

    @ns.doc(security=[{"sessionCookie": []}])
    @ns.expect(user_model)
    def post(self):
        data = request.get_json()
        new_user = AllowedUsersModel(email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return '', 200
    
    
@ns.route('/allowedUsers/<int:id>')
class Users(Resource):
    @ns.doc(security=[{"sessionCookie": []}])
    def delete(self, id):
        user = AllowedUsersModel.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 200