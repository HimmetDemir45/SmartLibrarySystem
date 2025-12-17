from library.repositories.category_repository import CategoryRepository
from library.models.category import Category
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    category_repo = CategoryRepository()

    @staticmethod
    def get_all_categories():
        try:
            return CategoryService.category_repo.get_all()
        except SQLAlchemyError as e:
            logger.error(f"Kategorileri getirme hatası: {str(e)}")
            raise

    @staticmethod
    def add_category(name):
        try:
            # Önce ismin boşluklarını temizle
            clean_name = name.strip() if name else ""
            if not clean_name:
                raise ValueError("Kategori adı boş olamaz.")

            # --- KONTROL: Bu isimde kategori zaten var mı? ---
            existing_category = CategoryService.category_repo.get_by_name(clean_name)
            if existing_category:
                # Varsa ekleme yapma, mevcut olanı döndür
                logger.info(f"Kategori zaten mevcut: {clean_name}")
                return existing_category

            # Yoksa yeni oluştur
            category = Category(name=clean_name)
            return CategoryService.category_repo.add(category)
        except ValueError as e:
            logger.error(f"Kategori ekleme validasyon hatası: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Kategori ekleme hatası: {str(e)}")
            raise

    @staticmethod
    def delete_category(category_id):
        try:
            category = CategoryService.category_repo.get_by_id(category_id)
            if not category:
                logger.warning(f"Kategori bulunamadı (category_id={category_id})")
                return False
            
            # Bağlı kitaplar var mı kontrol et (opsiyonel ama önerilir)
            from library.models.book import Book
            books_count = Book.query.filter_by(category_id=category_id).count()
            if books_count > 0:
                logger.warning(f"Kategori silinemiyor: {books_count} kitap bu kategoriye bağlı (category_id={category_id})")
                raise ValueError(f"Bu kategoriye bağlı {books_count} kitap bulunmaktadır. Önce kitapları silin veya kategorilerini değiştirin.")
            
            CategoryService.category_repo.delete(category)
            return True
        except ValueError as e:
            logger.error(f"Kategori silme validasyon hatası: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Kategori silme hatası (category_id={category_id}): {str(e)}")
            raise

    # Repository'nizde eksikse bu metodu eklemeniz gerekebilir
    # Ancak BookRepository'de benzerini yapmıştık, CategoryRepository'de de
    # find_by_name veya get_by_name olmalı.