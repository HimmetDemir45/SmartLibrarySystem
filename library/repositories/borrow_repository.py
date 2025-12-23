from library.models.borrow import Borrow
from library.models.book import Book
from library.repositories.base_repository import BaseRepository
from sqlalchemy.orm import joinedload

class BorrowRepository(BaseRepository):
    def __init__(self):
        super().__init__(Borrow)

    def get_active_borrow(self, user_id, book_id):
        """Bir kullanıcının belirli bir kitap için aktif (iade edilmemiş) kaydını bulur."""
        # Artık relationship'ler açıkça tanımlı, class-bound attribute kullanabiliriz
        return self.model.query.options(
            joinedload(Borrow.book).joinedload(Book.author),
            joinedload(Borrow.book).joinedload(Book.category),
            joinedload(Borrow.user)
        ).filter_by(user_id=user_id, book_id=book_id, return_date=None).first()

    def get_active_borrows_by_user(self, user_id):
        """Bir kullanıcının üzerindeki tüm aktif kitapları getirir."""
        return self.model.query.options(
            joinedload(Borrow.book).joinedload(Book.author),
            joinedload(Borrow.book).joinedload(Book.category),
            joinedload(Borrow.user)
        ).filter_by(user_id=user_id, return_date=None).all()

    def get_history_by_user(self, user_id):
        """Bir kullanıcının tüm ödünç geçmişini (aktif + iade edilmiş) getirir."""
        return self.model.query.options(
            joinedload(Borrow.book).joinedload(Book.author),
            joinedload(Borrow.book).joinedload(Book.category),
            joinedload(Borrow.user)
        ).filter_by(user_id=user_id).order_by(self.model.borrow_date.desc()).all()

    # --- EKSİK OLAN VE HATAYA SEBEP OLAN METOT ---
    def get_all_active(self):
        """Kütüphanedeki (herkesteki) iade edilmemiş tüm kitapları getirir."""
        return self.model.query.options(
            joinedload(Borrow.book).joinedload(Book.author),
            joinedload(Borrow.book).joinedload(Book.category),
            joinedload(Borrow.user)
        ).filter_by(return_date=None).all()