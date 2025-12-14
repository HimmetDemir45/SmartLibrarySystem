from library.repositories.borrow_repository import BorrowRepository
from library.repositories.book_repository import BookRepository
from library.models.borrow import Borrow
from datetime import datetime, timedelta
from library import db
from sqlalchemy import text

class LoanService:
    borrow_repo = BorrowRepository()
    book_repo = BookRepository()

    @staticmethod
    def borrow_book(user_id, book_id):
        book = LoanService.book_repo.get_by_id(book_id)

        if book and book.is_available:
            # Kitap durumunu güncelle
            book.is_available = False

            # Yeni ödünç kaydı oluştur
            due_date = datetime.utcnow() + timedelta(days=15)
            borrow_record = Borrow(user_id=user_id, book_id=book_id, due_date=due_date)

            # Repository ile kaydet
            LoanService.borrow_repo.add(borrow_record)
            # Kitap durumunu kaydet (BaseRepository.add zaten commit yapar ama garanti olsun)
            LoanService.book_repo.update()

            return {"success": True, "message": f"{book.name} ödünç alındı."}

        return {"success": False, "message": "Kitap şu an müsait değil veya bulunamadı."}

    @staticmethod
    def return_book(user_id, book_id):
        book = LoanService.book_repo.get_by_id(book_id)
        if not book:
            return {"success": False, "message": "Kitap bulunamadı."}

        # Aktif ödünç kaydını Repository'den iste
        active_borrow = LoanService.borrow_repo.get_active_borrow(user_id, book_id)

        if active_borrow:
            active_borrow.return_date = datetime.utcnow()
            book.is_available = True

            # Değişiklikleri kaydet (Trigger burada çalışacak)
            LoanService.borrow_repo.update()

            return {"success": True, "message": f"{book.name} iade edildi."}

        return {"success": False, "message": "Bu kitap zaten sizde görünmüyor."}

    @staticmethod
    def get_user_active_loans(user_id):
        # Repository'den Borrow listesi dönüyor, içinden kitapları çekiyoruz
        active_borrows = LoanService.borrow_repo.get_active_borrows_by_user(user_id)
        return [b.book for b in active_borrows]

    @staticmethod
    def get_user_history(user_id):
        return LoanService.borrow_repo.get_history_by_user(user_id)

    @staticmethod
    def calculate_total_fine(user_id):
        history = LoanService.borrow_repo.get_history_by_user(user_id)
        total = 0
        for record in history:
            if record.fine_amount:
                total += record.fine_amount
        return total

    @staticmethod
    def forgive_fines(user_id):
        try:
            # Stored Procedure çağrısı (Repository'e taşınabilir ama burada kalması da OK)
            db.session.execute(text("CALL sp_ForgiveFines(:p_id)"), {'p_id': user_id})
            db.session.commit()
            return True
        except Exception as e:
            print(f"Hata: {e}")
            return False