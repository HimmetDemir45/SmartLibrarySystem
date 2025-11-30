from library import app, db
from library.models import Book, Author, Category
from sqlalchemy import text

with app.app_context():
    print("Veritabanı temizleniyor...")

    # 1. MySQL'in güvenlik kilidini (Foreign Key) geçici olarak kapatıyoruz
    db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))

    # 2. Koddan sildiğimiz ama veritabanında kalan eski 'item' tablosunu manuel siliyoruz
    db.session.execute(text('DROP TABLE IF EXISTS item'))

    # 3. Geri kalan (User, Book, vb.) tabloları siliyoruz
    db.drop_all()

    # 4. Güvenlik kilidini tekrar açıyoruz
    db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))

    # 5. Yeni tabloları sıfırdan oluşturuyoruz
    db.create_all()

    # --- VERİ EKLEME BÖLÜMÜ ---

    # Yazarlar
    author1 = Author(name="J.K. Rowling")
    author2 = Author(name="George Orwell")
    author3 = Author(name="Fyodor Dostoevsky")

    # Kategoriler
    cat1 = Category(name="Fantastik")
    cat2 = Category(name="Bilim Kurgu")
    cat3 = Category(name="Klasik")

    db.session.add_all([author1, author2, author3, cat1, cat2, cat3])
    db.session.commit()

    # Kitaplar (Yazar ve Kategori ID'leri commit yapıldığı için oluştu)
    book1 = Book(name="Harry Potter", barcode="111111111111", description="Büyücülük okulu",
                 author_id=author1.id, category_id=cat1.id, is_available=True)

    book2 = Book(name="1984", barcode="222222222222", description="Distopik bir dünya",
                 author_id=author2.id, category_id=cat2.id, is_available=True)

    book3 = Book(name="Suç ve Ceza", barcode="333333333333", description="Vicdan muhasebesi",
                 author_id=author3.id, category_id=cat3.id, is_available=True)

    db.session.add_all([book1, book2, book3])
    db.session.commit()

    print("İŞLEM TAMAM: Eski tablolar silindi, yenileri kuruldu ve veriler eklendi.")