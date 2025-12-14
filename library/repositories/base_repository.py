from library import db

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_all(self):
        """Tüm kayıtları listeler"""
        return self.model.query.all()

    def get_by_id(self, id):
        """ID'ye göre tek kayıt getirir"""
        return self.model.query.get(id)

    def add(self, entity):
        """Yeni kayıt ekler ve kaydeder"""
        db.session.add(entity)
        db.session.commit()
        return entity

    def update(self):
        """Değişiklikleri kaydeder"""
        db.session.commit()

    def delete(self, entity):
        """Kaydı siler"""
        db.session.delete(entity)
        db.session.commit()