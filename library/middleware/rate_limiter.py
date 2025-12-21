"""
Rate Limiting Middleware - Brute Force koruması için
"""
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Basit in-memory rate limiting (Production'da Redis kullanılmalı)
_rate_limit_store = {}

class RateLimiter:
    """Basit rate limiting implementasyonu"""
    
    @staticmethod
    def is_rate_limited(key, max_attempts=5, window_seconds=300):
        """
        Rate limit kontrolü yapar
        key: Rate limit anahtarı (örn: IP adresi veya kullanıcı adı)
        max_attempts: Pencere içinde izin verilen maksimum deneme
        window_seconds: Pencere süresi (saniye)
        """
        now = datetime.now()
        
        if key not in _rate_limit_store:
            _rate_limit_store[key] = {
                'attempts': 0,
                'window_start': now
            }
            return False
        
        record = _rate_limit_store[key]
        
        # Pencere süresi dolmuşsa sıfırla
        if (now - record['window_start']).total_seconds() > window_seconds:
            record['attempts'] = 0
            record['window_start'] = now
            return False
        
        # Maksimum deneme sayısını aştı mı?
        if record['attempts'] >= max_attempts:
            remaining_time = window_seconds - (now - record['window_start']).total_seconds()
            logger.warning(f"Rate limit aşıldı: {key}, {remaining_time:.0f} saniye bekle")
            return True
        
        # Deneme sayısını artır
        record['attempts'] += 1
        return False
    
    @staticmethod
    def reset_rate_limit(key):
        """Rate limit kaydını sıfırla"""
        if key in _rate_limit_store:
            del _rate_limit_store[key]
    
    @staticmethod
    def get_client_ip():
        """İstemci IP adresini al"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr

def rate_limit(max_attempts=5, window_seconds=300, key_func=None):
    """
    Rate limiting decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if key_func:
                key = key_func()
            else:
                # Varsayılan olarak IP adresi kullan
                key = RateLimiter.get_client_ip()
            
            if RateLimiter.is_rate_limited(key, max_attempts, window_seconds):
                return jsonify({
                    'success': False,
                    'message': f'Çok fazla deneme yaptınız. Lütfen {window_seconds//60} dakika sonra tekrar deneyin.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

