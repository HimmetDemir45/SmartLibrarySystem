from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth_bp.login_page"
login_manager.login_message_category = "info"
login_manager.login_message = ""

migrate = Migrate(app, db) #  (Migrate'i başlatıyoruz)

from library.controllers.main_controller import main_bp
from library.controllers.auth_controller import auth_bp
from library.controllers.book_controller import book_bp
from library.controllers.admin_controller import admin_bp
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
app.register_blueprint(admin_bp)
