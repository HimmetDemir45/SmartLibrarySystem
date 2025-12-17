from library import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        """Tüm kayıtları listeler"""
        try:
            return self.model.query.all()
        except SQLAlchemyError as e:
            logger.error(f"Veritabanı hatası (get_all): {str(e)}")
            db.session.rollback()
            raise

    def get_by_id(self, id):
        """ID'ye göre tek kayıt getirir"""
        try:
            if id is None:
                logger.warning(f"get_by_id çağrıldı ancak id None")
                return None
            result = self.model.query.get(id)
            return result
        except SQLAlchemyError as e:
            logger.error(f"Veritabanı hatası (get_by_id, id={id}): {str(e)}")
            db.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Beklenmeyen hata (get_by_id, id={id}): {str(e)}")
            db.session.rollback()
            raise

    def add(self, entity):
        """Yeni kayıt ekler ve kaydeder"""
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Veritabanı hatası (add): {str(e)}")
            raise

    def update(self):
        """Değişiklikleri kaydeder"""
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Veritabanı hatası (update): {str(e)}")
            raise

    def delete(self, entity):
        """Kaydı siler"""
        try:
            db.session.delete(entity)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Veritabanı hatası (delete): {str(e)}")
            raise