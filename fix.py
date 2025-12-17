from library import app, db
from library.models.book import Book
from library.models.category import Category

def clean_categories():
    with app.app_context():
        print("--- Kategori Temizliği Başlıyor ---")

        # Tüm kategorileri al
        all_cats = Category.query.order_by(Category.id).all()
        seen_names = {} # { 'Roman': 1, 'Bilim': 5 } gibi tutacak

        deleted_count = 0

        for cat in all_cats:
            # İsimdeki boşlukları temizle (Örn: "Roman " -> "Roman")
            clean_name = cat.name.strip()

            if clean_name in seen_names:
                # Bu isimde daha önce bir kategori gördük (Bu bir kopya!)
                original_id = seen_names[clean_name]
                print(f"KOPYA BULUNDU: '{clean_name}' (ID: {cat.id}) -> Asıl ID: {original_id}'ye birleştiriliyor...")

                # 1. Bu kopya kategorideki kitapları bul ve asıl kategoriye taşı
                books_in_duplicate = Book.query.filter_by(category_id=cat.id).all()
                for book in books_in_duplicate:
                    book.category_id = original_id
                    print(f"  > Kitap Taşındı: {book.name}")

                # 2. Kitapları taşıdıktan sonra kopya kategoriyi sil
                db.session.delete(cat)
                deleted_count += 1

            else:
                # İlk kez görülen isim, bunu 'Asıl' olarak kaydet
                seen_names[clean_name] = cat.id

        db.session.commit()
        print(f"--- İşlem Tamamlandı. Toplam {deleted_count} adet kopya kategori silindi. ---")

if __name__ == '__main__':
    clean_categories()