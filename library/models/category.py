from library import db

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # İlişkiler
    books = db.relationship('Book', backref='category', lazy=True)

    def __repr__(self):
        return self.name