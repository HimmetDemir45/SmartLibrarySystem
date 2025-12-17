# Migration Rehberi

## Barcode Unique Constraint Kaldırma Migration'ı

Bu migration, `book` tablosundaki `barcode` alanının unique constraint'ini kaldırır. Böylece aynı kitaptan birden fazla kopya eklenebilir.

## Migration Çalıştırma Adımları

### 1. Migration Dosyasını Kontrol Et
Migration dosyası hazır: `migrations/versions/a1b2c3d4e5f6_remove_barcode_unique.py`

### 2. Mevcut Migration Durumunu Kontrol Et
```bash
flask db current
```
Bu komut şu anda hangi migration'ın aktif olduğunu gösterir.

### 3. Migration'ı Uygula
```bash
flask db upgrade
```

Bu komut:
- Tüm bekleyen migration'ları uygular
- `barcode` unique constraint'ini kaldırır
- Veritabanını günceller

### 4. Migration Durumunu Kontrol Et
```bash
flask db history
```
Bu komut tüm migration geçmişini gösterir.

### 5. Eğer Hata Alırsanız

#### SQLite Kullanıyorsanız:
SQLite bazı ALTER TABLE işlemlerini desteklemez. Bu durumda:

**Seçenek 1: Veritabanını Yeniden Oluştur (Önerilen)**
```bash
python seed.py
```
Bu komut veritabanını sıfırdan oluşturur ve tüm değişiklikleri uygular.

**Seçenek 2: Manuel Olarak Düzelt**
1. Veritabanı dosyasını yedekle (`instance/` klasöründeki `.db` dosyası)
2. Yeni bir migration oluştur:
```bash
flask db migrate -m "remove barcode unique"
```
3. Oluşan migration dosyasını düzenle ve `flask db upgrade` çalıştır

#### MySQL/PostgreSQL Kullanıyorsanız:
Migration otomatik olarak çalışmalı. Eğer sorun olursa:

```bash
# Migration'ı geri al
flask db downgrade

# Tekrar dene
flask db upgrade
```

## Alternatif: Veritabanını Yeniden Oluştur

Eğer veritabanında önemli veri yoksa, en kolay yol seed.py çalıştırmak:

```bash
python seed.py
```

Bu komut:
- Mevcut veritabanını siler
- Yeni tablolar oluşturur
- Seed data ekler
- Tüm değişiklikleri uygular

## Migration'ı Geri Alma

Eğer migration'ı geri almak isterseniz:

```bash
flask db downgrade
```

Bu komut son migration'ı geri alır ve unique constraint'i tekrar ekler.

## Sorun Giderme

### "Target database is not up to date" hatası
```bash
flask db stamp head
flask db upgrade
```

### "Can't locate revision identified by" hatası
Migration dosyasındaki `down_revision` değerini kontrol edin. Son migration'ın revision ID'si ile eşleşmeli.

### "Table already exists" hatası
Veritabanı zaten güncel olabilir. Durumu kontrol edin:
```bash
flask db current
```

