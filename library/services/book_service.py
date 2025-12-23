from library.repositories.book_repository import BookRepository
from library.repositories.author_repository import AuthorRepository
from library.repositories.category_repository import CategoryRepository
from library.models.book import Book
from library.models.author import Author
from library.models.category import Category
from library import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class BookService:
    # Depoları başlatıyoruz
    book_repo = BookRepository()
    author_repo = AuthorRepository()
    category_repo = CategoryRepository()

    @staticmethod
    def _get_or_create_author(author_input):
        """Yazar string veya Author objesi olabilir. Varsa getirir, yoksa oluşturur."""
        if isinstance(author_input, Author):
            return author_input

        if isinstance(author_input, str):
            author_obj = BookService.author_repo.get_by_name(author_input)
            if not author_obj:
                author_obj = Author(name=author_input)
                db.session.add(author_obj)
                db.session.flush()  # ID'yi almak için flush
            return author_obj

        raise ValueError(f"Geçersiz yazar tipi: {type(author_input)}")

    @staticmethod
    def _get_or_create_category(category_input):
        """Kategori string veya Category objesi olabilir. Varsa getirir, yoksa oluşturur."""
        if isinstance(category_input, Category):
            return category_input

        if isinstance(category_input, str):
            category_obj = BookService.category_repo.get_by_name(category_input)
            if not category_obj:
                category_obj = Category(name=category_input)
                db.session.add(category_obj)
                db.session.flush()  # ID'yi almak için flush
            return category_obj

        raise ValueError(f"Geçersiz kategori tipi: {type(category_input)}")

    @staticmethod
    def get_all_paginated(page=1, per_page=12):
        """Kitapları sayfalı şekilde getirir."""
        return BookService.book_repo.get_all_paginated(page=page, per_page=per_page)

    @staticmethod
    def get_all_books(page=1):
        return BookService.book_repo.get_all_paginated(page=page)

    @staticmethod
    def get_book_by_id(book_id):
        return BookService.book_repo.get_by_id(book_id)

    @staticmethod
    def search_books(query, page=1):
        return BookService.book_repo.search(query, page=page)

    @staticmethod
    def get_book_by_name(book_name):
        return BookService.book_repo.find_by_name(book_name)

    @staticmethod
    def add_book(name, author, category, barcode, description, image_file='default.jpg'):
        """Yeni bir kitap kaydı oluşturur."""
        try:
            # Helper metodları kullanarak yazar ve kategoriyi al/oluştur
            author_obj = BookService._get_or_create_author(author)
            category_obj = BookService._get_or_create_category(category)

            book_to_add = Book(
                name=name,
                barcode=barcode,
                description=description,
                image_file=image_file,
                author_id=author_obj.id,
                category_id=category_obj.id
            )

            db.session.add(book_to_add)
            db.session.commit()
            return book_to_add

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Kitap ekleme hatası: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Beklenmeyen hata (add_book): {str(e)}")
            raise

    @staticmethod
    def delete_book(book_id):
        try:
            book = BookService.book_repo.get_by_id(book_id)
            if book:
                # Eski resmi sil (default.jpg hariç)
                if book.image_file and book.image_file != 'default.jpg':
                    from library.services.file_service import FileService
                    FileService.delete_picture(book.image_file)

                BookService.book_repo.delete(book)
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Kitap silme hatası (book_id={book_id}): {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Beklenmeyen hata (delete_book): {str(e)}")
            raise

    @staticmethod
    def update_book(book_id, data):
        try:
            book = BookService.book_repo.get_by_id(book_id)
            if not book:
                return None

            old_image_file = book.image_file  # Eski resmi sakla

            # Temel Bilgiler
            if 'name' in data and data['name']:
                book.name = data['name']
            if 'barcode' in data and data['barcode']:
                book.barcode = data['barcode']
            if 'description' in data and data['description']:
                book.description = data['description']

            # Resim güncelleme
            if 'image_file' in data and data['image_file']:
                # Yeni resim varsa eski resmi sil (default.jpg hariç)
                if old_image_file and old_image_file != 'default.jpg' and old_image_file != data['image_file']:
                    from library.services.file_service import FileService
                    FileService.delete_picture(old_image_file)
                book.image_file = data['image_file']

            # İlişkisel Veriler (Yazar/Kategori) - Helper metodları kullan
            if 'author' in data and data['author']:
                author_obj = BookService._get_or_create_author(data['author'])
                book.author_id = author_obj.id

            if 'category' in data and data['category']:
                category_obj = BookService._get_or_create_category(data['category'])
                book.category_id = category_obj.id

            # Değişiklikleri kaydet
            db.session.commit()
            return book

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Kitap güncelleme hatası (book_id={book_id}): {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Beklenmeyen hata (update_book): {str(e)}")
            raise

    @staticmethod
    def get_book_by_barcode(barcode):
        return BookService.book_repo.find_by_barcode(barcode)
