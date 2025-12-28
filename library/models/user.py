from library import db, login_manager, bcrypt
from flask_login import UserMixin
# --- YENİ EKLENEN İMPORTLAR ---
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer

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

    @property
    def password(self):
        raise AttributeError('password özelliği okunamayan bir alandır!')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    # --- EKSİK OLAN FONKSİYONLAR BURADA ---

    def get_reset_token(self):
        # Token üretir (Şifre sıfırlama linki için)
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        # Token doğrular ve kullanıcıyı bulur
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'<User {self.username}>'