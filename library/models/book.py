from library import db

class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False)  # unique=True kaldırıldı - aynı kitaptan birden fazla eklenebilir
    description = db.Column(db.String(length=1024), nullable=False)

    # YENİ EKLENEN SATIR: Resim dosyası adı (Varsayılan olarak 'default.jpg' olsun)
    image_file = db.Column(db.String(60), nullable=False, default='default.jpg') # <-- Yeni

    is_available = db.Column(db.Boolean, default=True)

    # İlişkiler
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # borrows relationship'i Borrow modelindeki backref ile oluşturuluyor
    # borrows = db.relationship('Borrow', backref='book', lazy=True)  # Artık Borrow modelinde tanımlı

    def __repr__(self):
        return f'{self.name}'