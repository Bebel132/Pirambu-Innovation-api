from extensions import db

class BiographyModel(db.Model):
    __tablename__ = 'biography'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text, nullable=True)
    file = db.Column(db.LargeBinary, nullable=True)
    
    def json(self):
        return {
            'description': self.description,
            'hasFile': self.file is not None,
        }