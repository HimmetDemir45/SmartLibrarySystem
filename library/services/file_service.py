import os
import secrets
from PIL import Image
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class FileService:
    """Dosya ve resim işleme görevlerini yönetir."""

    @staticmethod
    def save_picture(form_picture):
        """Yüklenen resmi diske kaydeder ve rastgele ismini döndürür."""
        try:
            if not form_picture or not form_picture.filename:
                logger.warning("Resim dosyası boş veya geçersiz")
                return 'default.jpg'

            # 8 karakterlik rastgele hex isim oluştur
            random_hex = secrets.token_hex(8)

            # Dosya uzantısını al
            _, f_ext = os.path.splitext(form_picture.filename)
            if not f_ext:
                f_ext = '.jpg'  # Varsayılan uzantı
            
            # Güvenlik: Sadece izin verilen uzantılar
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            if f_ext.lower() not in allowed_extensions:
                logger.warning(f"İzin verilmeyen dosya uzantısı: {f_ext}")
                return 'default.jpg'
            
            picture_fn = random_hex + f_ext.lower()

            # Kaydedilecek tam yolu belirle
            picture_dir = os.path.join(current_app.root_path, 'static', 'book_pics')
            
            # Klasör yoksa oluştur
            if not os.path.exists(picture_dir):
                os.makedirs(picture_dir)
            
            picture_path = os.path.join(picture_dir, picture_fn)

            # Resmi boyutlandır
            output_size = (250, 400)
            i = Image.open(form_picture)
            
            # Resmi RGB'ye çevir
            if i.mode != 'RGB':
                i = i.convert('RGB')
            
            i.thumbnail(output_size, Image.Resampling.LANCZOS)

            # Resmi kaydet
            i.save(picture_path, 'JPEG', quality=85)
            
            logger.info(f"Resim başarıyla kaydedildi: {picture_fn}")
            return picture_fn
            
        except Exception as e:
            logger.error(f"Resim kaydetme hatası: {str(e)}")
            return 'default.jpg'

    @staticmethod
    def delete_picture(filename):
        """Resim dosyasını siler."""
        try:
            if not filename or filename == 'default.jpg':
                return False
            
            picture_path = os.path.join(
                current_app.root_path, 
                'static', 
                'book_pics', 
                filename
            )
            
            if os.path.exists(picture_path):
                os.remove(picture_path)
                logger.info(f"Resim silindi: {filename}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Resim silme hatası ({filename}): {str(e)}")
            return False