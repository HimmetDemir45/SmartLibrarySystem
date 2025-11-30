from library import app, db
from library.models import Book, Author, Category
from sqlalchemy import text

with app.app_context():
    print("Veritabanı temizleniyor...")

    # 1. Güvenlik kilidini aç
    db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))

    # 2. Eski tablo, trigger ve prosedürleri temizle
    db.session.execute(text('DROP TABLE IF EXISTS item')) # Eski market tablosu
    db.session.execute(text('DROP TRIGGER IF EXISTS calc_fine_on_return'))
    db.session.execute(text('DROP PROCEDURE IF EXISTS sp_ForgiveFines'))

    db.drop_all()

    # 3. Tabloları oluştur
    db.create_all()

    # --- SQL TRIGGER OLUŞTURMA ---
    # Görev: Kitap iade edildiğinde (borrow tablosu güncellendiğinde) cezayı otomatik hesapla.
    # Mantık: Eğer iade tarihi (return_date), son tarihten (due_date) büyükse; aradaki gün farkını 5 ile çarp.
    print("Trigger oluşturuluyor...")
    trigger_sql = """
                  CREATE TRIGGER calc_fine_on_return
                      BEFORE UPDATE ON borrow
                      FOR EACH ROW
                  BEGIN
                      IF NEW.return_date IS NOT NULL THEN
            IF NEW.return_date > NEW.due_date THEN
                SET NEW.fine_amount = DATEDIFF(NEW.return_date, NEW.due_date) * 5.0;
                      ELSE
                SET NEW.fine_amount = 0.0;
                  END IF;
                  END IF;
                  END; \
                  """
    db.session.execute(text(trigger_sql))

    # --- STORED PROCEDURE OLUŞTURMA ---
    # Görev: Belirli bir kullanıcının tüm cezalarını sıfırla (Af yetkisi).
    print("Procedure oluşturuluyor...")
    procedure_sql = """
                    CREATE PROCEDURE sp_ForgiveFines(IN p_user_id INT)
                    BEGIN
                    UPDATE borrow SET fine_amount = 0 WHERE user_id = p_user_id;
                    END; \
                    """
    db.session.execute(text(procedure_sql))

    # 4. Güvenlik kilidini kapat
    db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))

    # --- VERİ EKLEME ---
    author1 = Author(name="J.K. Rowling")
    author2 = Author(name="George Orwell")
    author3 = Author(name="Fyodor Dostoevsky")

    cat1 = Category(name="Fantastik")
    cat2 = Category(name="Bilim Kurgu")
    cat3 = Category(name="Klasik")

    db.session.add_all([author1, author2, author3, cat1, cat2, cat3])
    db.session.commit()

    book1 = Book(name="Harry Potter", barcode="111111111111", description="Büyücülük okulu",
                 author_id=author1.id, category_id=cat1.id, is_available=True)
    book2 = Book(name="1984", barcode="222222222222", description="Distopik bir dünya",
                 author_id=author2.id, category_id=cat2.id, is_available=True)
    book3 = Book(name="Suç ve Ceza", barcode="333333333333", description="Vicdan muhasebesi",
                 author_id=author3.id, category_id=cat3.id, is_available=True)

    db.session.add_all([book1, book2, book3])
    db.session.commit()

    print("İŞLEM TAMAM: Tablolar, Trigger ve Procedure başarıyla kuruldu.")