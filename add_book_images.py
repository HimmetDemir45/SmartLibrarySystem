"""
Kitap resimlerini otomatik olarak eklemek için yardımcı script
Bu script default.jpg'i tüm kitaplara kopyalar veya özel resimler ekler
"""

import os
import shutil
from library import app, db
from library.models import Book

def setup_book_images():
    """Tüm kitaplara default resim atar"""
    with app.app_context():
        books = Book.query.all()
        default_image_path = os.path.join('library', 'static', 'book_pics', 'default.jpg')
        
        if not os.path.exists(default_image_path):
            print("⚠ UYARI: default.jpg bulunamadı!")
            print(f"Lütfen {default_image_path} dosyasının var olduğundan emin olun.")
            return
        
        print(f"📚 {len(books)} kitap bulundu")
        print("🖼️  Resimler kontrol ediliyor...")
        
        updated_count = 0
        for book in books:
            if book.image_file == 'default.jpg':
                continue  # Zaten default.jpg kullanıyor
            
            # Eğer resim dosyası yoksa default.jpg'e geç
            image_path = os.path.join('library', 'static', 'book_pics', book.image_file)
            if not os.path.exists(image_path):
                book.image_file = 'default.jpg'
                updated_count += 1
                print(f"  ✓ {book.name} -> default.jpg")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ {updated_count} kitap güncellendi")
        else:
            print("\n✅ Tüm kitapların resimleri mevcut")

if __name__ == '__main__':
    setup_book_images()

