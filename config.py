# config.py
import os

class Config:
    SECRET_KEY = 'ec9439cfc6c796ae2029594d' # Bunu güvenli bir şey yap
    # MySQL bağlantı adresin (Şifreni ve kullanıcı adını buraya yaz)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:2993@localhost/newschema'
    SQLALCHEMY_TRACK_MODIFICATIONS = False