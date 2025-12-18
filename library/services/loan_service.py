from library.repositories.user_repository import UserRepository
from library.repositories.borrow_repository import BorrowRepository
from library.repositories.book_repository import BookRepository
from library.models.borrow import Borrow
from datetime import datetime, timedelta, timezone
from library import db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class LoanService:
    borrow_repo = BorrowRepository()
    book_repo = BookRepository()

    @staticmethod
    def borrow_book(user_id, book_id):
        try:
            # 1. KULLANICI ONAY KONTROLÜ
            user_repo = UserRepository()
            user = user_repo.get_by_id(user_id)

            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı."}

            # Eğer admin değilse ve onayı yoksa engelle
            if not user.is_admin and not user.is_approved:
                return {
                    "success": False,
                    "message": "⚠️ İşlem Başarısız: Kitap ödünç alabilmek için üyeliğinizin yönetici tarafından onaylanması gerekmektedir. Lütfen onay bekleyin."
                }

            # 2. KULLANICI KİTAP LİMİTİ KONTROLÜ
            max_books = current_app.config.get('MAX_BOOKS_PER_USER', 5)
            active_loans_count = LoanService.borrow_repo.get_active_borrows_by_user(user_id)
            if len(active_loans_count) >= max_books:
                return {
                    "success": False,
                    "message": f"⚠️ Maksimum kitap limitine ulaştınız! Aynı anda en fazla {max_books} kitap alabilirsiniz. Lütfen önce bir kitap iade edin."
                }

            # 3. Kitap işlemleri
            book = LoanService.book_repo.get_by_id_with_lock(book_id)

            if not book:
                return {"success": False, "message": "Kitap bulunamadı."}

            if not book.is_available:
                return {"success": False, "message": "Kitap şu an müsait değil."}

            # 4. ÖDÜNÇ KAYDINI OLUŞTUR
            borrow_date = datetime.now(timezone.utc)
            # Ödünç süresini config'den al
            loan_period = current_app.config.get('LOAN_PERIOD_DAYS', 15)
            due_date = borrow_date + timedelta(days=loan_period)
            
            new_borrow = Borrow(
                user_id=user_id,
                book_id=book_id,
                borrow_date=borrow_date,
                due_date=due_date,
                fine_amount=0.0
            )
            
            # 4. Kitabı "Müsait Değil" yap
            book.is_available = False
            
            # 5. Değişiklikleri kaydet
            db.session.add(new_borrow)
            db.session.commit()
            
            logger.info(f"Kitap ödünç verildi | user_id={user_id}, book_id={book_id}, due_date={due_date}")
            
            return {
                "success": True, 
                "message": f"{book.name} başarıyla ödünç alındı. İade tarihi: {due_date.strftime('%d.%m.%Y')}"
            }

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Ödünç alma hatası (user_id={user_id}, book_id={book_id}): {str(e)}")
            return {"success": False, "message": "Bir hata oluştu. Lütfen tekrar deneyin."}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Beklenmeyen hata (borrow_book): {str(e)}")
            return {"success": False, "message": "Bir hata oluştu. Lütfen tekrar deneyin."}

    @staticmethod
    def pay_fines_via_budget(user_id):
        """
        Kullanıcının bütçesinden cezayı düşer ve borçlarını siler.
        Hepsi tek bir 'transaction' içinde yapılır.
        """
        try:
            user_repo = UserRepository()
            user = user_repo.get_by_id(user_id)

            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı."}

            # 1. Toplam cezayı hesapla
            total_fine = LoanService.calculate_total_fine(user_id)

            if total_fine <= 0:
                return {"success": False, "message": "Ödenecek cezanız bulunmuyor."}

            # 2. Bütçe kontrolü
            if user.budget < total_fine:
                return {"success": False,
                        "message": f"Yetersiz bakiye! (Gereken: {total_fine} TL, Mevcut: {user.budget} TL)"}

            # 3. İŞLEM: Hem parayı düş hem cezayı sil
            user.budget -= total_fine  # Bütçeden düş

            # Aktif cezalari sil (ORM ile)
            from library.models.borrow import Borrow
            active_borrows = Borrow.query.filter_by(user_id=user_id, return_date=None).all()
            for borrow in active_borrows:
                borrow.fine_amount = 0

            # Geçmişteki ödenmemiş cezaları da sıfırlayabilirsiniz (Opsiyonel)
            # ...

            db.session.commit()  # Tek seferde kaydet
            return {"success": True, "message": "Ödeme başarıyla alındı ve borçlarınız silindi."}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Ödeme hatası (user_id={user_id}): {str(e)}")
            return {"success": False, "message": "Veritabanı hatası oluştu."}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Beklenmeyen ödeme hatası: {str(e)}")
            return {"success": False, "message": "İşlem sırasında bir hata oluştu."}

    # --- GÜNCELLENMİŞ CEZA AFFETME (Admin İçin) ---
    @staticmethod
    def forgive_fines(user_id):
        try:
            # Stored Procedure yerine Python ORM kullanıyoruz
            from library.models.borrow import Borrow

            # Sadece aktif borçlardaki cezaları sıfırlıyoruz
            active_borrows = Borrow.query.filter_by(user_id=user_id, return_date=None).all()

            # Eğer hiç ceza/borç yoksa bile True dönebiliriz veya kontrol edebiliriz
            count = 0
            for borrow in active_borrows:
                if borrow.fine_amount > 0:
                    borrow.fine_amount = 0
                    count += 1

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Cezaları affetme hatası (user_id={user_id}): {str(e)}")
            return False

    # ... (Geri kalan return_book, get_user_active_loans vb. metodları aynen kalabilir) ...
    @staticmethod
    def return_book(user_id, book_id):
        try:
            book = LoanService.book_repo.get_by_id(book_id)
            logger.info(f"İade işlemi başladı | user_id={user_id}, book_id={book_id}, book={book}")
            if not book:
                logger.warning(f"İade işlemi - kitap bulunamadı | user_id={user_id}, book_id={book_id}")
                return {"success": False, "message": "Kitap bulunamadı."}

            active_borrow = LoanService.borrow_repo.get_active_borrow(user_id, book_id)
            logger.info(f"Aktif ödünç sorgusu: {active_borrow}")

            if not active_borrow:
                # Detaylıca hangi kayıtlar var göster
                from library.models.borrow import Borrow
                open_borrows = Borrow.query.filter_by(book_id=book_id, user_id=user_id, return_date=None).all()
                logger.error(
                    f"İade işlemi için aktif borç bulunamadı. DB'de return_date=None ile görünen kayıtlar: {open_borrows}")
                return {"success": False, "message": "Bu kitap zaten sizde görünmüyor."}

            now = datetime.now(timezone.utc)
            logger.info(f"İade zamanı: {now}, Önceki return_date: {active_borrow.return_date}")
            active_borrow.return_date = now
            book.is_available = True

            # Gecikme cezası hesaplama
            fine_amount = 0.0
            if active_borrow.due_date:
                due_date = active_borrow.due_date
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=timezone.utc)
                logger.info(f"Due Date: {due_date}, Bugün: {now}")
                if now > due_date:
                    days_overdue = (now - due_date).days
                    daily_fee = current_app.config.get('DAILY_FINE', 50.0)
                    fine_amount = days_overdue * daily_fee
                    active_borrow.fine_amount = fine_amount
                    logger.info(
                        f"Gecikme cezası hesaplandı: {fine_amount} TL ({days_overdue} gün) - User: {user_id}, Book: {book_id}")

            # Tek transaction içinde kaydet
            logger.info(f"Veritabanı commit öncesi | active_borrow: {active_borrow}, fine_amount: {fine_amount}")
            db.session.commit()
            logger.info(f"Veritabanı commit sonrası | active_borrow: {active_borrow}")

            message = f"{book.name} iade edildi."
            if fine_amount > 0:
                message += f" Gecikme cezası: {fine_amount:.2f} TL"

            logger.info(
                f"İade işlemi başarıyla tamamlandı | user_id={user_id}, book_id={book_id}, fine_amount={fine_amount}")
            return {"success": True, "message": message, "fine_amount": fine_amount}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"İade hatası (user_id={user_id}, book_id={book_id}): {str(e)}", exc_info=True)
            return {"success": False, "message": "Bir hata oluştu. Lütfen tekrar deneyin."}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Beklenmeyen hata (return_book): {str(e)}", exc_info=True)
            return {"success": False, "message": "Bir hata oluştu. Lütfen tekrar deneyin."}

    @staticmethod
    def get_user_active_loans(user_id):
        active_borrows = LoanService.borrow_repo.get_active_borrows_by_user(user_id)
        return [b.book for b in active_borrows]

    @staticmethod
    def get_user_history(user_id):
        return LoanService.borrow_repo.get_history_by_user(user_id)

    @staticmethod
    def calculate_total_fine(user_id):
        """Sadece aktif (iade edilmemiş) borçlardaki cezaları hesaplar"""
        active_borrows = LoanService.borrow_repo.get_active_borrows_by_user(user_id)
        total = 0.0
        now = datetime.now(timezone.utc)
        daily_fee = current_app.config.get('DAILY_FINE', 50.0)
        
        for borrow in active_borrows:
            # Mevcut ceza miktarını al
            fine = borrow.fine_amount or 0.0
            
            # Eğer due_date geçmişse, güncel cezayı hesapla
            if borrow.due_date:
                due_date = borrow.due_date
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=timezone.utc)
                
                if now > due_date:
                    days_overdue = (now - due_date).days
                    current_fine = days_overdue * daily_fee
                    # Mevcut cezadan büyükse güncelle
                    if current_fine > fine:
                        fine = current_fine
            
            total += fine
        
        return total

    @staticmethod
    def get_all_active_loans_with_fine():
        active_borrows = LoanService.borrow_repo.get_all_active()

        # Config'den günlük ceza miktarını çekiyoruz
        daily_fee = current_app.config.get('DAILY_FINE', 1.0)

        results = []
        now = datetime.now(timezone.utc)

        for borrow in active_borrows:
            current_fine = 0.0
            days_overdue = 0

            if borrow.due_date:
                # Offset-naive datetime'ı offset-aware'a çevir
                due_date = borrow.due_date
                if due_date.tzinfo is None:
                    # Eğer timezone bilgisi yoksa UTC olarak kabul et
                    due_date = due_date.replace(tzinfo=timezone.utc)

                if now > due_date:
                    delta = now - due_date
                    days_overdue = delta.days

                    # Dinamik hesaplama
                    current_fine = days_overdue * daily_fee

            results.append({
                'borrow': borrow,
                'days_overdue': days_overdue,
                'current_fine': current_fine
            })

        return results
