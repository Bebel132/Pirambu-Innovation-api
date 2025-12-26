from extensions import db

class EventsModel(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file = db.Column(db.LargeBinary, nullable=True)
    active = db.Column(db.Boolean, nullable=True, default=True)
    is_draft = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'hasFile': self.file is not None,
            'is_draft': self.is_draft,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }