from library import db

class Author(db.Model):
    __tablename__ = 'author'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # İlişkiler
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return self.name