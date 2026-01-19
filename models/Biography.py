from extensions import db

class BiographyModel(db.Model):
    __tablename__ = 'biography'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.Text, nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    file = db.Column(db.LargeBinary, nullable=True)
    
    def json(self):
        return {
            'description': self.description,
            'instagram': self.instagram,
            'whatsapp': self.whatsapp,
            'endereco': self.endereco,
            'hasFile': self.file is not None,
        }