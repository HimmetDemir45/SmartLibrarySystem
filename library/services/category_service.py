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
            clean_name = name.strip()

            # --- KONTROL: Bu isimde kategori zaten var mı? ---
            existing_category = CategoryService.category_repo.get_by_name(clean_name)
            if existing_category:
                # Varsa ekleme yapma, mevcut olanı döndür (veya False döndür)
                return existing_category

            # Yoksa yeni oluştur
            category = Category(name=clean_name)
            return CategoryService.category_repo.add(category)
        except SQLAlchemyError as e:
            logger.error(f"Kategori ekleme hatası: {str(e)}")
            raise

    @staticmethod
    def delete_category(category_id):
        try:
            category = CategoryService.category_repo.get_by_id(category_id)
            if category:
                CategoryService.category_repo.delete(category)
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Kategori silme hatası (category_id={category_id}): {str(e)}")
            raise

    # Repository'nizde eksikse bu metodu eklemeniz gerekebilir
    # Ancak BookRepository'de benzerini yapmıştık, CategoryRepository'de de
    # find_by_name veya get_by_name olmalı.