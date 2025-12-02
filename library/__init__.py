from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2993@localhost/newschema'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
app.config['WTF_CSRF_ENABLED'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"
login_manager.login_message = ""  # Burayı ekledik, artık uyarı çıkmayacak.
from library import routes

with app.app_context():
    db.create_all()
