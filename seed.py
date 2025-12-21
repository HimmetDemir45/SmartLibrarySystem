from library import app, db, bcrypt
from library.models import Book, Author, Category, User, Borrow
from sqlalchemy import text
from datetime import datetime, timedelta, timezone

with app.app_context():
    print("=" * 60)
    print("VERİTABANI YENİDEN OLUŞTURULUYOR...")
    print("=" * 60)

    # 1. Güvenlik kilidini aç (MySQL için)
    try:
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    except:
        pass  # SQLite kullanılıyorsa bu komut çalışmaz

    # 2. Eski tablo, trigger ve prosedürleri temizle
    try:
        db.session.execute(text('DROP TABLE IF EXISTS item'))
        db.session.execute(text('DROP TRIGGER IF EXISTS calc_fine_on_return'))
        db.session.execute(text('DROP PROCEDURE IF EXISTS sp_ForgiveFines'))
    except:
        pass

    db.drop_all()

    # 3. Tabloları oluştur
    db.create_all()
    print("✓ Tablolar oluşturuldu")

    # --- SQL TRIGGER OLUŞTURMA (MySQL için) ---
    try:
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
                      END;
                      """
        db.session.execute(text(trigger_sql))
        print("✓ Trigger oluşturuldu")
    except Exception as e:
        print(f"⚠ Trigger oluşturulamadı: {e}")

    # --- STORED PROCEDURE OLUŞTURMA (MySQL için) ---
    try:
        print("Procedure oluşturuluyor...")
        procedure_sql = """
                        CREATE PROCEDURE sp_ForgiveFines(IN p_user_id INT)
                        BEGIN
                            UPDATE borrow SET fine_amount = 0 WHERE user_id = p_user_id;
                        END;
                        """
        db.session.execute(text(procedure_sql))
        print("✓ Procedure oluşturuldu")
    except Exception as e:
        print(f"⚠ Procedure oluşturulamadı: {e}")

    # 4. Güvenlik kilidini kapat
    try:
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
    except:
        pass

    # --- KULLANICILAR ---
    print("\nKullanıcılar oluşturuluyor...")
    admin_user = User(
        username="admin",
        email_address="admin@kutuphane.com",
        password="admin123",  # bcrypt otomatik hash'leyecek
        is_admin=True,
        budget=0
    )
    
    user1 = User(
        username="ahmet",
        email_address="ahmet@example.com",
        password="123456",
        is_admin=False,
        budget=0
    )
    
    user2 = User(
        username="ayse",
        email_address="ayse@example.com",
        password="123456",
        is_admin=False,
        budget=0
    )

    db.session.add_all([admin_user, user1, user2])
    db.session.commit()
    print("✓ Kullanıcılar oluşturuldu (admin/admin123, ahmet/123456, ayse/123456)")

    # --- YAZARLAR ---
    print("\nYazarlar oluşturuluyor...")
    authors = [
        Author(name="J.K. Rowling"),
        Author(name="George Orwell"),
        Author(name="Fyodor Dostoevsky"),
        Author(name="Orhan Pamuk"),
        Author(name="Yaşar Kemal"),
        Author(name="Isaac Asimov"),
        Author(name="J.R.R. Tolkien"),
        Author(name="Haruki Murakami"),
        Author(name="Gabriel García Márquez"),
        Author(name="Virginia Woolf")
    ]
    db.session.add_all(authors)
    db.session.commit()
    print(f"✓ {len(authors)} yazar eklendi")

    # --- KATEGORİLER ---
    print("\nKategoriler oluşturuluyor...")
    categories = [
        Category(name="Fantastik"),
        Category(name="Bilim Kurgu"),
        Category(name="Klasik"),
        Category(name="Roman"),
        Category(name="Tarih"),
        Category(name="Biyografi"),
        Category(name="Felsefe"),
        Category(name="Şiir"),
        Category(name="Çocuk"),
        Category(name="Polisiye")
    ]
    db.session.add_all(categories)
    db.session.commit()
    print(f"✓ {len(categories)} kategori eklendi")

    # --- KİTAPLAR ---
    print("\nKitaplar oluşturuluyor...")
    books = [
        # Fantastik
        Book(name="Harry Potter ve Felsefe Taşı", barcode="111111111111", 
             description="Büyücülük okulunda maceralı bir yolculuk", 
             author_id=authors[0].id, category_id=categories[0].id, is_available=True),
        Book(name="Harry Potter ve Sırlar Odası", barcode="121212121212", 
             description="Hogwarts'ta ikinci yıl", 
             author_id=authors[0].id, category_id=categories[0].id, is_available=True),
        Book(name="Harry Potter ve Azkaban Tutsağı", barcode="131313131313", 
             description="Sirius Black'in hikayesi", 
             author_id=authors[0].id, category_id=categories[0].id, is_available=True),
        Book(name="Yüzüklerin Efendisi: Yüzük Kardeşliği", barcode="777777777777", 
             description="Orta Dünya'da epik bir macera", 
             author_id=authors[6].id, category_id=categories[0].id, is_available=True),
        Book(name="Yüzüklerin Efendisi: İki Kule", barcode="141414141414", 
             description="Orta Dünya'nın kaderi", 
             author_id=authors[6].id, category_id=categories[0].id, is_available=True),
        Book(name="Hobbit", barcode="151515151515", 
             description="Bilbo Baggins'in macerası", 
             author_id=authors[6].id, category_id=categories[0].id, is_available=True),
        
        # Bilim Kurgu
        Book(name="1984", barcode="222222222222", 
             description="Distopik bir gelecek tasviri", 
             author_id=authors[1].id, category_id=categories[1].id, is_available=True),
        Book(name="Vakıf", barcode="666666666666", 
             description="Galaktik imparatorluk ve gelecek", 
             author_id=authors[5].id, category_id=categories[1].id, is_available=True),
        Book(name="Vakıf ve İmparatorluk", barcode="161616161616", 
             description="Vakıf serisinin ikinci kitabı", 
             author_id=authors[5].id, category_id=categories[1].id, is_available=True),
        Book(name="Ben Robot", barcode="171717171717", 
             description="Robotik ve etik üzerine", 
             author_id=authors[5].id, category_id=categories[1].id, is_available=True),
        Book(name="Dune", barcode="181818181818", 
             description="Çöl gezegeni Arrakis'in hikayesi", 
             author_id=authors[5].id, category_id=categories[1].id, is_available=True),
        
        # Klasik
        Book(name="Suç ve Ceza", barcode="333333333333", 
             description="Vicdan muhasebesi ve ahlaki sorgulama", 
             author_id=authors[2].id, category_id=categories[2].id, is_available=True),
        Book(name="Hayvan Çiftliği", barcode="191919191919", 
             description="Allegorik bir siyasi hiciv", 
             author_id=authors[1].id, category_id=categories[2].id, is_available=True),
        Book(name="Savaş ve Barış", barcode="202020202020", 
             description="Napolyon dönemi Rusya'sı", 
             author_id=authors[2].id, category_id=categories[2].id, is_available=True),
        Book(name="Anna Karenina", barcode="212121212121", 
             description="Aşk ve toplumsal kurallar", 
             author_id=authors[2].id, category_id=categories[2].id, is_available=True),
        Book(name="Madame Bovary", barcode="222222222223", 
             description="Fransız edebiyatının başyapıtı", 
             author_id=authors[2].id, category_id=categories[2].id, is_available=True),
        
        # Roman
        Book(name="Kara Kitap", barcode="444444444444", 
             description="İstanbul'da geçen gizemli bir hikaye", 
             author_id=authors[3].id, category_id=categories[3].id, is_available=True),
        Book(name="İnce Memed", barcode="555555555555", 
             description="Anadolu'dan bir destan", 
             author_id=authors[4].id, category_id=categories[3].id, is_available=True),
        Book(name="Kumandanı Öldürmek", barcode="888888888888", 
             description="Japon edebiyatından bir başyapıt", 
             author_id=authors[7].id, category_id=categories[3].id, is_available=True),
        Book(name="Yüzyıllık Yalnızlık", barcode="999999999999", 
             description="Latin Amerika edebiyatının şaheseri", 
             author_id=authors[8].id, category_id=categories[3].id, is_available=True),
        Book(name="Beyaz Kale", barcode="232323232323", 
             description="Osmanlı döneminde bir hikaye", 
             author_id=authors[3].id, category_id=categories[3].id, is_available=True),
        Book(name="Masumiyet Müzesi", barcode="242424242424", 
             description="Aşk ve koleksiyonculuk", 
             author_id=authors[3].id, category_id=categories[3].id, is_available=True),
        Book(name="Yılanların Öcü", barcode="252525252525", 
             description="Köy hayatından kesitler", 
             author_id=authors[4].id, category_id=categories[3].id, is_available=True),
        Book(name="1Q84", barcode="262626262626", 
             description="Alternatif bir dünya", 
             author_id=authors[7].id, category_id=categories[3].id, is_available=True),
        
        # Tarih
        Book(name="Osmanlı Tarihi", barcode="272727272727", 
             description="Osmanlı İmparatorluğu'nun tarihi", 
             author_id=authors[4].id, category_id=categories[4].id, is_available=True),
        Book(name="Türkiye Tarihi", barcode="282828282828", 
             description="Türkiye'nin modern tarihi", 
             author_id=authors[4].id, category_id=categories[4].id, is_available=True),
        
        # Felsefe
        Book(name="Kendine Ait Bir Oda", barcode="101010101010", 
             description="Kadın yazarlar ve edebiyat üzerine", 
             author_id=authors[9].id, category_id=categories[6].id, is_available=True),
        Book(name="Sofie'nin Dünyası", barcode="292929292929", 
             description="Felsefe tarihine yolculuk", 
             author_id=authors[9].id, category_id=categories[6].id, is_available=True),
        
        # Polisiye
        Book(name="Sherlock Holmes: Kızıl Dosya", barcode="303030303030", 
             description="Ünlü dedektifin maceraları", 
             author_id=authors[5].id, category_id=categories[9].id, is_available=True),
        Book(name="Agatha Christie: Ölüm Sessiz Geldi", barcode="313131313131", 
             description="Gizem dolu bir cinayet", 
             author_id=authors[5].id, category_id=categories[9].id, is_available=True),
        
        # Çocuk
        Book(name="Küçük Prens", barcode="323232323232", 
             description="Büyüklere masal", 
             author_id=authors[7].id, category_id=categories[8].id, is_available=True),
        Book(name="Alice Harikalar Diyarında", barcode="333333333334", 
             description="Fantastik bir macera", 
             author_id=authors[7].id, category_id=categories[8].id, is_available=True),
        
        # Şiir
        Book(name="Divan-ı Hikmet", barcode="343434343434", 
             description="Tasavvuf şiirleri", 
             author_id=authors[4].id, category_id=categories[7].id, is_available=True),
    ]
    db.session.add_all(books)
    db.session.commit()
    print(f"✓ {len(books)} kitap eklendi")

    # --- ÖRNEK ÖDÜNÇ KAYITLARI (Timezone-aware datetime ile) ---
    print("\nÖrnek ödünç kayıtları oluşturuluyor...")
    now = datetime.now(timezone.utc)
    
    # Aktif ödünç kayıtları (henüz iade edilmemiş)
    borrow1 = Borrow(
        user_id=user1.id,
        book_id=books[0].id,
        borrow_date=now - timedelta(days=10),
        due_date=now + timedelta(days=5),
        return_date=None,
        fine_amount=0.0
    )
    books[0].is_available = False
    
    # Gecikmiş ödünç kaydı (ceza hesaplanacak)
    borrow2 = Borrow(
        user_id=user2.id,
        book_id=books[1].id,
        borrow_date=now - timedelta(days=20),
        due_date=now - timedelta(days=5),  # 5 gün gecikmiş
        return_date=None,
        fine_amount=0.0
    )
    books[1].is_available = False
    
    # İade edilmiş kayıt
    borrow3 = Borrow(
        user_id=user1.id,
        book_id=books[2].id,
        borrow_date=now - timedelta(days=30),
        due_date=now - timedelta(days=15),
        return_date=now - timedelta(days=14),  # Zamanında iade edilmiş
        fine_amount=0.0
    )
    
    db.session.add_all([borrow1, borrow2, borrow3])
    db.session.commit()
    print("✓ Örnek ödünç kayıtları eklendi")

    print("\n" + "=" * 60)
    print("VERİTABANI BAŞARIYLA OLUŞTURULDU!")
    print("=" * 60)
    print("\nGiriş Bilgileri:")
    print("  Admin: admin / admin123")
    print("  Kullanıcı 1: ahmet / 123456")
    print("  Kullanıcı 2: ayse / 123456")
    print("\nToplam:")
    print(f"  - {len(authors)} Yazar")
    print(f"  - {len(categories)} Kategori")
    print(f"  - {len(books)} Kitap")
    print(f"  - {len([admin_user, user1, user2])} Kullanıcı")
    print(f"  - 3 Ödünç Kaydı")
    print("=" * 60)