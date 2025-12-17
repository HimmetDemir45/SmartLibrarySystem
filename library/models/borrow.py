from library import db
from datetime import datetime, timezone

class Borrow(db.Model):
    __tablename__ = 'borrow'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    borrow_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    return_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)

    fine_amount = db.Column(db.Float, default=0.0)

    # İlişkiler (backref'ler yerine açıkça tanımlıyoruz)
    user = db.relationship('User', backref='borrows', lazy=True)
    book = db.relationship('Book', backref='borrows', lazy=True)

    def __repr__(self):
        return f'<Borrow {self.id}>'