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
            new_author = Author(name=name)
            return AuthorService.author_repo.add(new_author)
        except SQLAlchemyError as e:
            logger.error(f"Yazar ekleme hatası: {str(e)}")
            raise

    @staticmethod
    def update_author(author_id, new_name):
        try:
            author = AuthorService.author_repo.get_by_id(author_id)
            if author:
                author.name = new_name
                AuthorService.author_repo.update()
                return True
            return False
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