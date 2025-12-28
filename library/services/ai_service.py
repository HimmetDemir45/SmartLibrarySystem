import requests
import logging
from library.services.book_service import BookService
from library.services.loan_service import LoanService
from library.services.stats_service import StatsService

logger = logging.getLogger(__name__)


class AIService:
    """Ollama AI servisi - DeepSeek-R1:8b modeli ile entegrasyon"""

    OLLAMA_BASE_URL = "http://localhost:11434"
    MODEL_NAME = "deepseek-r1:8b"

    @staticmethod
    def _call_ollama(prompt, system_prompt=None, max_tokens=1000):
        """Ollama API'sine istek gönderir"""
        try:
            url = f"{AIService.OLLAMA_BASE_URL}/api/generate"

            payload = {
                "model": AIService.MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "").strip()

        except requests.exceptions.ConnectionError:
            logger.error("Ollama servisine bağlanılamadı. Ollama çalışıyor mu?")
            return "Üzgünüm, AI asistanı şu anda kullanılamıyor. Lütfen Ollama servisinin çalıştığından emin olun."
        except requests.exceptions.Timeout:
            logger.error("Ollama API zaman aşımına uğradı")
            return "Üzgünüm, istek zaman aşımına uğradı. Lütfen tekrar deneyin."
        except Exception as e:
            logger.error(f"Ollama API hatası: {str(e)}")
            return f"Bir hata oluştu: {str(e)}"

    @staticmethod
    def _get_library_context():
        """Kütüphane hakkında genel bilgileri toplar"""
        try:
            stats = StatsService.get_library_stats()
            if not stats:
                return ""

            context = f"""
                Kütüphane İstatistikleri:
                - Toplam Kitap: {stats.get('total_books', 0)}
                - Müsait Kitap: {stats.get('available_books', 0)}
                - Ödünç Alınan: {stats.get('borrowed_books', 0)}
                - Toplam Üye: {stats.get('total_users', 0)}
                """
            return context
        except Exception as e:
            logger.error(f"Kütüphane bağlamı alınamadı: {str(e)}")
            return ""

    @staticmethod
    def _get_user_context(user_id):
        """Kullanıcı hakkında bilgileri toplar (öneriler için)"""
        try:
            user_stats = StatsService.get_user_stats(user_id)
            if not user_stats:
                return ""

            active_books = LoanService.get_user_active_loans(user_id)
            active_book_names = [book.name for book in active_books[:5]]

            context = f"""
                Kullanıcı Bilgileri:
                - Toplam Ödünç: {user_stats.get('total_borrows', 0)}
                - Aktif Kitap: {user_stats.get('active_borrows', 0)}
                - Şu an okunan kitaplar: {', '.join(active_book_names) if active_book_names else 'Yok'}
                """

            if user_stats.get('favorite_categories'):
                categories = ', '.join([cat['name'] for cat in user_stats['favorite_categories']])
                context += f"- Favori kategoriler: {categories}\n"

            return context
        except Exception as e:
            logger.error(f"Kullanıcı bağlamı alınamadı: {str(e)}")
            return ""

    @staticmethod
    def _get_books_context(limit=50, include_recent=True):
        """Kütüphanedeki kitaplar hakkında bilgi - Her çağrıda güncel verileri çeker"""
        try:
            # Yeni eklenen kitapları öncelikli göstermek için ID'ye göre azalan sıralama
            # (yeni kitaplar genelde daha yüksek ID'ye sahip)
            from library.models.book import Book
            from sqlalchemy.orm import joinedload

            if include_recent:
                # En yeni kitapları önce getir (ID'ye göre azalan)
                recent_books = Book.query.options(
                    joinedload(Book.author),
                    joinedload(Book.category)
                ).order_by(Book.id.desc()).limit(limit).all()
            else:
                # Normal sıralama ile getir
                books_pagination = BookService.get_all_paginated(page=1, per_page=limit)
                recent_books = books_pagination.items if books_pagination else []

            if not recent_books:
                return ""

            books_list = []
            for book in recent_books:
                author_name = book.author.name if book.author else 'Bilinmiyor'
                category_name = book.category.name if book.category else 'Genel'

                # BURASI YENİ: Kitabın açıklamasını veritabanından çekip AI'ya veriyoruz
                description = book.description if book.description else "Bu kitap hakkında detaylı açıklama girilmemiş."

                # AI'ya gidecek metni zenginleştiriyoruz
                book_info = f"""
                    Kitap: {book.name}
                    Yazar: {author_name}
                    Kategori: {category_name}
                    Özet ve Konu: {description}
                    -------------------"""
            
            books_list.append(f"- {book.name} (Yazar: {author_name}, Kategori: {category_name})\n  Konu: {description}")

            context = f"Kütüphanemizdeki Mevcut Kitaplar ve Detayları:\n"
            context += "\n".join(books_list)



            return context
        except Exception as e:
            logger.error(f"Kitaplar bağlamı alınamadı: {str(e)}")
            return ""

    @staticmethod
    def _is_library_related(message):
        """Kullanıcının sorusunun kütüphane ile ilgili olup olmadığını kontrol eder"""
        library_keywords = [
            'kitap', 'yazar', 'kategori', 'kütüphane', 'okuma', 'öneri', 'ödünç',
            'iade', 'emanet', 'roman', 'hikaye', 'edebiyat', 'yayın', 'yayınevi',
            'barkod', 'raflar', 'katalog', 'koleksiyon', 'okur', 'okuyucu'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in library_keywords)

    @staticmethod
    def chat(user_id, message):
        """Genel sohbet için AI yanıtı - Her çağrıda güncel kitapları çeker"""
        # Kütüphane ile ilgili mi kontrol et
        is_library_question = AIService._is_library_related(message)

        if is_library_question:
            # Kütüphane soruları için detaylı sistem prompt
            system_prompt = """Sen 'Himmet Kütüphanesi'nin uzman asistanısın. Adın 'Bilge'.
                Kuralların:
                1. Sadece Türkçe cevap ver.
                2. Kullanıcıya her zaman ismiyle veya 'Sayın Üye' diyerek hitap et.
                3. Kitap önerirken sadece sana verilen listedeki kitapları kullan, uydurma.
                4. Eğer sorunun cevabı kütüphane verilerinde yoksa, dürüstçe 'Bu konuda bilgim yok' de.
                5. Cevapların kısa, teşvik edici ve nazik olsun.
                6. Asla kod, SQL sorgusu veya teknik detay paylaşma.
            """

            library_context = AIService._get_library_context()
            # Güncel kitapları çek (yeni eklenenler dahil)
            books_context = AIService._get_books_context(limit=30, include_recent=True)

            prompt = f"""
{library_context}

{books_context}

Kullanıcı sorusu: {message}

Lütfen kullanıcının sorusunu yanıtla. Eğer belirli bir kitap veya yazar hakkında soru sorulduysa, yukarıdaki GÜNCEL kitap listesini kullan.
Yeni eklenen kitaplar da bu listede yer alır. Bu bir kütüphane sorusudur, detaylı cevap ver.
"""
        else:
            # Kütüphane dışı sorular için kısa ve öz sistem prompt
            system_prompt = """Sen bir kütüphane asistanısın ama genel konularda da yardımcı olabilirsin.
Türkçe yanıt ver. Ancak önceliğin kütüphane konularıdır. 
Kütüphane dışı sorulara kısa ve öz cevap ver (2-3 cümle). Çok detaya girme.
Eğer soru kütüphane dışındaysa, kısa cevap verip kütüphane konularına yönlendirebilirsin."""

            # Kütüphane dışı sorular için minimal bağlam
            library_context = AIService._get_library_context()

            prompt = f"""
{library_context}

Kullanıcı sorusu: {message}

Bu soru kütüphane konusu dışında görünüyor. Kısa ve öz cevap ver (2-3 cümle).
Çok detaya girmeme. İstersen kütüphane konularına yönlendirebilirsin ama zorunlu değil.
"""

        return AIService._call_ollama(prompt, system_prompt)

    @staticmethod
    def get_book_recommendations(user_id):
        """Kullanıcıya kitap önerileri yapar - Güncel kitapları kullanır"""
        system_prompt = """Sen bir kütüphane asistanısın. Kullanıcının okuma geçmişine göre kişiselleştirilmiş kitap önerileri sunuyorsun.
Türkçe yanıt ver. Her öneri için kısa bir açıklama yap. Yeni eklenen kitapları da önerebilirsin."""

        user_context = AIService._get_user_context(user_id)
        library_context = AIService._get_library_context()
        # Tüm kitapları çek (yeni eklenenler dahil)
        books_context = AIService._get_books_context(limit=50, include_recent=True)

        prompt = f"""
{library_context}

{user_context}

{books_context}

Kullanıcıya okuma geçmişine ve tercihlerine göre 5-7 kitap öner. Her kitap için kısa bir açıklama yap ve neden önerdiğini belirt.
Sadece yukarıdaki GÜNCEL listede bulunan kitapları öner. Yeni eklenen kitapları da değerlendirebilirsin.
"""

        return AIService._call_ollama(prompt, system_prompt, max_tokens=800)

    @staticmethod
    def get_book_info(book_name):
        """Belirli bir kitap hakkında bilgi verir - Güncel veritabanından çeker"""
        system_prompt = """Sen bir kütüphane asistanısın. Kitaplar hakkında detaylı bilgi veriyorsun.
Türkçe yanıt ver. Kitap hakkında yazar, kategori, konu ve özellikler hakkında bilgi ver."""

        # Güncel veritabanından kitabı bul
        book = BookService.get_book_by_name(book_name)
        if not book:
            # Arama yap (güncel kitaplar dahil)
            search_results = BookService.search_books(book_name, page=1)
            if search_results and search_results.items:
                book = search_results.items[0]
            else:
                # Son bir deneme: Tüm kitapları kontrol et
                books_context = AIService._get_books_context(limit=100, include_recent=True)
                if book_name.lower() in books_context.lower():
                    return f"'{book_name}' adlı kitap kütüphanede bulundu ancak detaylı bilgi alınamadı. Lütfen AI asistanına sorun: '{book_name} hakkında bilgi verir misin?'"
                return f"'{book_name}' adlı kitap kütüphanede bulunamadı. Yeni eklenen kitaplar da dahil olmak üzere tüm kitaplar kontrol edildi."

        # Güncel kitaplar bağlamı
        books_context = AIService._get_books_context(limit=20, include_recent=True)

        prompt = f"""
{books_context}

Kullanıcı şu kitap hakkında bilgi istiyor: {book.name}

Kitap Bilgileri (Güncel):
- Adı: {book.name}
- Yazar: {book.author.name if book.author else 'Bilinmiyor'}
- Kategori: {book.category.name if book.category else 'Genel'}
- Açıklama: {book.description}

Bu kitap hakkında detaylı bilgi ver. Kitabın konusu, yazarı hakkında bilgi ve neden okunması gerektiği hakkında konuş.
"""

        return AIService._call_ollama(prompt, system_prompt)

    @staticmethod
    def get_author_info(author_name):
        """Yazar hakkında bilgi verir"""
        system_prompt = """Sen Türk edebiyatına ve dünya klasiklerine hakim uzman bir kütüphanecisin.
        Sana sorulan yazarları veritabanındaki kitaplarla eşleştir.
        ANCAK, eğer veritabanında yazarın biyografisi yoksa, KENDİ GENEL KÜLTÜRÜNÜ KULLAN.
        Yaşar Kemal, Orhan Pamuk, Sabahattin Ali gibi önemli yazarlar sorulduğunda, veritabanına bağlı kalmadan hayatları ve edebi kişilikleri hakkında detaylı, uzun ve doyurucu bilgi ver.
        Cevabın Türkçe, ansiklopedik ama samimi olsun"""

        # Yazarı bul
        from library.repositories.author_repository import AuthorRepository
        author_repo = AuthorRepository()
        author = author_repo.get_by_name(author_name)

        if not author:
            return f"'{author_name}' adlı yazar kütüphanede bulunamadı."

        # Yazarın kitaplarını bul
        books = BookService.search_books(author_name, page=1)
        author_books = []
        if books and books.items:
            for book in books.items:
                if book.author and book.author.name.lower() == author_name.lower():
                    author_books.append(book.name)

        books_context = AIService._get_books_context(limit=20)

        prompt = f"""
{books_context}

Kullanıcı şu yazar hakkında bilgi istiyor: {author.name}

Yazarın Kütüphanedeki Kitapları: {', '.join(author_books) if author_books else 'Bulunamadı'}

Bu yazar hakkında detaylı bilgi ver. Yazarın hayatı, edebi tarzı, önemli eserleri ve neden okunması gerektiği hakkında konuş.
"""

        return AIService._call_ollama(prompt, system_prompt)

    @staticmethod
    def check_ollama_connection():
        """Ollama servisinin çalışıp çalışmadığını kontrol eder"""
        try:
            url = f"{AIService.OLLAMA_BASE_URL}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            return AIService.MODEL_NAME in model_names
        except Exception as e:
            logger.error(f"Ollama bağlantı kontrolü hatası: {str(e)}")
            return False
