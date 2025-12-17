# Kitap Resimleri Ekleme Rehberi

## Resim Ekleme Yöntemleri

### Yöntem 1: Hazır Resimler Kullanma (Önerilen)

1. **Resim İndirme Siteleri:**
   - [Unsplash](https://unsplash.com) - Ücretsiz, yüksek kaliteli resimler
   - [Pexels](https://www.pexels.com) - Ücretsiz stok fotoğraflar
   - [Pixabay](https://pixabay.com) - Ücretsiz resimler

2. **Arama Terimleri:**
   - "book cover"
   - "library books"
   - "reading book"
   - Kitap isimleri (örn: "Harry Potter book")

3. **Resim Formatı:**
   - Format: JPG, PNG, JPEG
   - Boyut: 300x400px veya daha büyük (oran korunmalı)
   - Dosya boyutu: Mümkünse 500KB altında

### Yöntem 2: Otomatik Resim Ekleme Script'i

`add_book_images.py` script'ini kullanarak otomatik olarak default resimleri kopyalayabilirsiniz.

### Yöntem 3: Manuel Ekleme

1. Resimleri `library/static/book_pics/` klasörüne kopyalayın
2. Dosya adını kitap ID'si veya benzersiz bir isimle kaydedin
3. Admin panelinden kitabı düzenleyip resmi seçin

## Mevcut Resimler

- `default.jpg` - Varsayılan kitap resmi (tüm kitaplar için kullanılır)
- Diğer resimler kitap ID'sine göre otomatik atanır

## Notlar

- Tüm kitaplar için `default.jpg` kullanılabilir
- Özel resim eklemek isterseniz admin panelinden kitap eklerken resim yükleyebilirsiniz
- Resimler otomatik olarak optimize edilir

