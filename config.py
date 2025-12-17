import os
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yüklüyoruz
load_dotenv()

class Config:
    # Artık şifreler kodun içinde değil, ortam değişkenlerinden geliyor
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Eğer .env okunamazsa hata vermemesi için varsayılan bir değer bırakabilir
    # veya None kontrolü yapabilirsiniz.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True