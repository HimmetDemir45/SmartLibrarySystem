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
        # --- DÜZELTME: get_by_id yerine get_by_id_with_lock kullanıyoruz ---
        # Bu satır çalıştığı anda, veritabanındaki kitap satırı kilitlenir.
        book = LoanService.book_repo.get_by_id_with_lock(book_id)

        if book and book.is_available:
            # Kitap durumunu güncelle
            book.is_available = False

            # Yeni ödünç kaydı oluştur
            due_date = datetime.utcnow() + timedelta(days=15)
            borrow_record = Borrow(user_id=user_id, book_id=book_id, due_date=due_date)

            # Repository ile kaydet
            LoanService.borrow_repo.add(borrow_record)

            # --- ÖNEMLİ ---
            # Kitap durumunu güncelliyoruz. update() çağrılıp transaction commit edildiğinde
            # kilit otomatik olarak kalkar ve sırada bekleyen diğer kullanıcı devam eder.
            LoanService.book_repo.update()

            return {"success": True, "message": f"{book.name} ödünç alındı."}

        return {"success": False, "message": "Kitap şu an müsait değil veya bulunamadı."}

    # ... (Geri kalan return_book, get_user_active_loans vb. metodları aynen kalabilir) ...
    @staticmethod
    def return_book(user_id, book_id):
        book = LoanService.book_repo.get_by_id(book_id)
        if not book:
            return {"success": False, "message": "Kitap bulunamadı."}

        active_borrow = LoanService.borrow_repo.get_active_borrow(user_id, book_id)

        if active_borrow:
            active_borrow.return_date = datetime.utcnow()
            book.is_available = True
            LoanService.borrow_repo.update()
            return {"success": True, "message": f"{book.name} iade edildi."}

        return {"success": False, "message": "Bu kitap zaten sizde görünmüyor."}

    @staticmethod
    def get_user_active_loans(user_id):
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
            db.session.execute(text("CALL sp_ForgiveFines(:p_id)"), {'p_id': user_id})
            db.session.commit()
            return True
        except Exception as e:
            print(f"Hata: {e}")
            return False

    @staticmethod
    def get_all_active_loans_with_fine():
        """Tüm aktif ödünçleri çeker ve anlık ceza durumunu hesaplar."""
        active_borrows = LoanService.borrow_repo.get_all_active()

        results = []
        for borrow in active_borrows:
            current_fine = 0.0
            days_overdue = 0

            # Eğer son teslim tarihi geçmişse
            if borrow.due_date and datetime.utcnow() > borrow.due_date:
                delta = datetime.utcnow() - borrow.due_date
                days_overdue = delta.days
                # ÖRNEK: Günlük 2.5 TL ceza varsayalım (Bunu değiştirebilirsiniz)
                current_fine = days_overdue * 2.5

            results.append({
                'borrow': borrow,  # Ödünç kaydı (kitap ve user bilgisi içinde)
                'days_overdue': days_overdue,
                'current_fine': current_fine
            })

        return results
