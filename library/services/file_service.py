
import os
import secrets
from PIL import Image
from flask import current_app

class FileService:
    """Dosya ve resim işleme görevlerini yönetir."""

    @staticmethod
    def save_picture(form_picture):
        """Yüklenen resmi diske kaydeder ve rastgele ismini döndürür."""

        # 8 karakterlik rastgele hex isim oluştur
        random_hex = secrets.token_hex(8)

        # Dosya uzantısını al
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext

        # Kaydedilecek tam yolu belirle
        # current_app.root_path, Flask uygulamasının ana dizinidir
        picture_path = os.path.join(current_app.root_path, 'static/book_pics', picture_fn)

        # Resmi boyutlandır (Örn: 250x400 pixel)
        output_size = (250, 400)
        i = Image.open(form_picture)
        i.thumbnail(output_size)

        # Resmi kaydet
        i.save(picture_path)

        return picture_fn