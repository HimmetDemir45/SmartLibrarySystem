import time
import sys
import os

# Proje dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from library import app, db
from library.models.book import Book
from library.services.ai_service import AIService

def generate_book_descriptions():
    """
    Veritabanındaki tüm kitapları tarar ve DeepSeek kullanarak
    her biri için detaylı açıklamalar oluşturur.
    Veritabanı limitine (1024 karakter) uygun şekilde kırpar.
    """
    print("="*60)
    print("KİTAP AÇIKLAMALARINI GÜNCELLEME SİSTEMİ (LİMİT KORUMALI)")
    print("Model: DeepSeek-R1:8b")
    print("="*60)

    with app.app_context():
        # Tüm kitapları çek
        books = Book.query.all()
        total_books = len(books)

        print(f"Toplam {total_books} kitap bulundu. İşlem başlıyor...\n")

        for index, book in enumerate(books, 1):
            # Hata durumunda session bozulmasın diye her kitapta güvenli blok
            try:
                author_name = book.author.name if book.author else "Bilinmiyor"
                print(f"[{index}/{total_books}] İşleniyor: {book.name} ({author_name})")

                # AI için prompt
                prompt = f"""
                    Kitap Adı: {book.name}
                    Yazarı: {author_name}
                    
                    GÖREV:
                    Bu kitap için kütüphane kataloğunda kullanılacak profesyonel, edebi bir tanıtım metni yaz.
                    
                    KURALLAR:
                    1. Türkçe yaz.
                    2. Spoiler verme.
                    3. ÇOK UZUN YAZMA. En fazla 150 kelime olsun.
                    4. Doğrudan tanıtıma gir.
                    """
                system_prompt = "Sen öz ve etkileyici yazan bir kütüphane uzmanısın."

                # AI servisini çağır
                description = AIService._call_ollama(prompt, system_prompt, max_tokens=800)

                if description and "hata" not in description.lower():
                    description = description.strip()

                    # KRİTİK DÜZELTME: Karakter Limiti Kontrolü
                    # Veritabanı limitiniz 1024. Güvenlik için 1000'de kesiyoruz.
                    if len(description) > 1000:
                        description = description[:1000] + "..."
                        print("   ! Uyarı: Açıklama çok uzundu, veritabanı limiti için kısaltıldı.")

                    book.description = description
                    db.session.commit()
                    print(f"   ✓ Güncellendi ({len(description)} karakter).")
                else:
                    print(f"   ! Açıklama üretilemedi.")

            except Exception as e:
                db.session.rollback()  # ÖNEMLİ: Hatayı temizle ki sonraki kitaplar etkilenmesin
                print(f"   X Hata oluştu: {str(e)}")

            # Bilgisayarı yormamak için kısa bekleme
            time.sleep(1)

    print("\n" + "="*60)
    print("İŞLEM TAMAMLANDI!")
    print("="*60)

if __name__ == "__main__":
    response = input("İşlemi başlatmak istiyor musunuz? (e/h): ")
    if response.lower() == 'e':
        generate_book_descriptions()
    else:
        print("İşlem iptal edildi.")