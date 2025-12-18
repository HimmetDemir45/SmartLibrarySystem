from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth_bp.login_page"
login_manager.login_message_category = "info"
login_manager.login_message = ""

migrate = Migrate(app, db) #  (Migrate'i başlatıyoruz)

# Logging konfigürasyonu
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/library.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Library uygulaması başlatıldı')

from library.controllers.main_controller import main_bp
from library.controllers.auth_controller import auth_bp
from library.controllers.book_controller import book_bp
from library.controllers.admin_controller import admin_bp
from library.controllers.api_controller import api_bp
from library.controllers.ai_controller import ai_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(ai_bp)