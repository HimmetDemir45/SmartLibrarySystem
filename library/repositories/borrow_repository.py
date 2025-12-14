from library.repositories.base_repository import BaseRepository
from library.models.borrow import Borrow
from library.models.book import Book

class BorrowRepository(BaseRepository):
    def __init__(self):
        super().__init__(Borrow)

    def get_active_borrow(self, user_id, book_id):
        """Kullanıcının belirli bir kitap için iade etmediği kaydı bulur"""
        return self.model.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            return_date=None
        ).first()

    def get_active_borrows_by_user(self, user_id):
        """Kullanıcının elindeki tüm kitapları (Borrow nesnesi olarak) getirir"""
        return self.model.query.filter_by(
            user_id=user_id,
            return_date=None
        ).all()

    def get_history_by_user(self, user_id):
        """Kullanıcının tüm geçmişini getirir (Yeniden eskiye)"""
        return self.model.query.filter_by(user_id=user_id).order_by(
            self.model.borrow_date.desc()
        ).all()

    def count_active_loans(self):
        """Toplam aktif ödünç sayısını verir (Dashboard için)"""
        return self.model.query.filter_by(return_date=None).count()