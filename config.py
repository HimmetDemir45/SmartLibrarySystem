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
    
    # Kütüphane Kuralları
    DAILY_FINE = float(os.getenv('DAILY_FINE', 50))  # Bulamazsa varsayılan 50 TL
    MAX_BOOKS_PER_USER = int(os.getenv('MAX_BOOKS_PER_USER', 5))  # Kullanıcı başına max kitap
    LOAN_PERIOD_DAYS = int(os.getenv('LOAN_PERIOD_DAYS', 15))  # Ödünç süresi (gün)
    
    # Ollama AI Ayarları
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'deepseek-r1:8b')