from extensions import db

class AllowedUsersModel(db.Model):
    __tablename__ = 'allowedUsers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def json(self):
        return {
            'id': self.id,
            'email': self.email,
        }