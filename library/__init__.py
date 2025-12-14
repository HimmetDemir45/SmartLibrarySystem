from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate  # <-- 1. BU SATIRI EKLE

app = Flask(__name__)
# Config dosyasından ayarları çekmesi için şu satırı eklemeniz iyi olur:
# app.config.from_object('config.Config')
# Ancak mevcut yapınızda elle atadığınız için şimdilik dokunmuyorum:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2993@localhost/newschema'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
app.config['WTF_CSRF_ENABLED'] = True # Config dosyasını kullanmıyorsanız buradan da True yapın.

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth_bp.login_page"
login_manager.login_message_category = "info"
login_manager.login_message = ""

migrate = Migrate(app, db) # <-- 2. BU SATIRI EKLE (Migrate'i başlatıyoruz)

from library.controllers.main_controller import main_bp
from library.controllers.auth_controller import auth_bp
from library.controllers.book_controller import book_bp
# from library.controllers.api_controller import api_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
# app.register_blueprint(api_bp)

# 3. AŞAĞIDAKİ create_all SATIRLARINI SİLİN VEYA YORUMA ALIN
# Çünkü artık tabloları "flask db upgrade" komutuyla oluşturacağız.
# with app.app_context():
#     db.create_all()