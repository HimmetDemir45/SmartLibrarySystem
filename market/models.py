from market import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Kullanıcı Tablosu
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    # Admin yetkisi için boolean alan (PDF Madde 7 gereği)
    is_admin = db.Column(db.Boolean, default=False)

    # İlişkiler
    borrows = db.relationship('Borrow', backref='user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

# Yazar Tablosu (PDF Madde 4 gereği)
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return self.name

# Kategori Tablosu (PDF Madde 4 gereği)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    books = db.relationship('Book', backref='category', lazy=True)

    def __repr__(self):
        return self.name

# Kitap Tablosu (Eski Item)
class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False)
    # Market mantığı (fiyat) yerine kütüphane ilişkileri
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # Kitap şu an kütüphanede mi yoksa birinde mi?
    is_available = db.Column(db.Boolean, default=True)

    borrows = db.relationship('Borrow', backref='book', lazy=True)

    def __repr__(self):
        return f'{self.name}'

# Ödünç Alma ve Ceza Takibi Tablosu (PDF Madde 6 gereği)
class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Alış tarihi
    return_date = db.Column(db.DateTime, nullable=True) # İade ettiği tarih
    due_date = db.Column(db.DateTime, nullable=False) # Teslim etmesi gereken son tarih

    # Ceza hesaplama için (Gecikme varsa buraya yazılacak)
    fine_amount = db.Column(db.Float, default=0.0)