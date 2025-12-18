from library import db, login_manager, bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    budget = db.Column(db.Integer(), nullable=False, default=0)
    is_approved = db.Column(db.Boolean, default=False)
    # İlişkiler (backref Borrow modelinde tanımlı)
    # borrows relationship'i Borrow modelindeki backref ile oluşturuluyor

    @property
    def password(self):
        # Şifrenin okunabilir bir özellik olmadığını belirtiyoruz
        raise AttributeError('password özelliği okunamayan bir alandır!')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def __repr__(self):
        return f'<User {self.username}>'

