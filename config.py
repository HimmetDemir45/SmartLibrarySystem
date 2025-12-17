import os
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yüklüyoruz
load_dotenv()

class Config:
    # Artık şifreler kodun içinde değil, ortam değişkenlerinden geliyor
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Config validation - kritik değerler kontrol ediliyor
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY ortam değişkeni ayarlanmamış! Lütfen .env dosyasını kontrol edin.")

    # Eğer .env okunamazsa hata vermemesi için varsayılan bir değer bırakabilir
    # veya None kontrolü yapabilirsiniz.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URI ortam değişkeni ayarlanmamış! Lütfen .env dosyasını kontrol edin.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    DAILY_FINE = float(os.getenv('DAILY_FINE', 50)) # Bulamazsa varsayılan 50 TL