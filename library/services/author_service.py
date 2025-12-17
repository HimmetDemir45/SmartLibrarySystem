from library.repositories.author_repository import AuthorRepository
from library.models.author import Author
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class AuthorService:
    author_repo = AuthorRepository()

    @staticmethod
    def get_all_authors():
        try:
            return AuthorService.author_repo.get_all()
        except SQLAlchemyError as e:
            logger.error(f"Yazarları getirme hatası: {str(e)}")
            raise

    @staticmethod
    def get_author_by_id(author_id):
        try:
            return AuthorService.author_repo.get_by_id(author_id)
        except SQLAlchemyError as e:
            logger.error(f"Yazar getirme hatası (author_id={author_id}): {str(e)}")
            raise

    @staticmethod
    def add_author(name):
        try:
            # İsim boşluklarını temizle
            clean_name = name.strip() if name else ""
            if not clean_name:
                raise ValueError("Yazar adı boş olamaz.")
            
            # Aynı isimde yazar var mı kontrol et
            existing_author = AuthorService.author_repo.get_by_name(clean_name)
            if existing_author:
                logger.info(f"Yazar zaten mevcut: {clean_name}")
                return existing_author
            
            new_author = Author(name=clean_name)
            return AuthorService.author_repo.add(new_author)
        except ValueError as e:
            logger.error(f"Yazar ekleme validasyon hatası: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Yazar ekleme hatası: {str(e)}")
            raise

    @staticmethod
    def update_author(author_id, new_name):
        try:
            clean_name = new_name.strip() if new_name else ""
            if not clean_name:
                raise ValueError("Yazar adı boş olamaz.")
            
            author = AuthorService.author_repo.get_by_id(author_id)
            if not author:
                logger.warning(f"Yazar bulunamadı (author_id={author_id})")
                return False
            
            # Aynı isimde başka bir yazar var mı kontrol et
            existing_author = AuthorService.author_repo.get_by_name(clean_name)
            if existing_author and existing_author.id != author_id:
                logger.warning(f"Bu isimde başka bir yazar zaten mevcut: {clean_name}")
                return False
            
            author.name = clean_name
            AuthorService.author_repo.update()
            return True
        except ValueError as e:
            logger.error(f"Yazar güncelleme validasyon hatası: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Yazar güncelleme hatası (author_id={author_id}): {str(e)}")
            raise

    @staticmethod
    def delete_author(author_id):
        # NOT: Silmeden önce bu yazarın kitaba bağlı olup olmadığını kontrol etmeniz gerekebilir.
        try:
            author = AuthorService.author_repo.get_by_id(author_id)
            if author:
                AuthorService.author_repo.delete(author)
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Yazar silme hatası (author_id={author_id}): {str(e)}")
            raise