from extensions import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    username = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    picture = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def json(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'username': self.username,
            'email': self.email,
            'picture': self.picture,
            'created_at': self.created_at.isoformat()
        }