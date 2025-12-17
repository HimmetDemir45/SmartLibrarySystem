from library import db
from library.models import Borrow, Book
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Bildirim servisi - gecikmiş kitaplar, yaklaşan son tarihler vb."""

    @staticmethod
    def get_overdue_notifications(user_id=None):
        """Gecikmiş kitaplar için bildirimler"""
        try:
            now = datetime.now(timezone.utc)
            query = Borrow.query.filter_by(return_date=None)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            overdue_borrows = []
            for borrow in query.all():
                if borrow.due_date:
                    due_date = borrow.due_date
                    if due_date.tzinfo is None:
                        due_date = due_date.replace(tzinfo=timezone.utc)
                    
                    if now > due_date:
                        days_overdue = (now - due_date).days
                        overdue_borrows.append({
                            'borrow': borrow,
                            'days_overdue': days_overdue,
                            'book_name': borrow.book.name if borrow.book else 'Bilinmeyen'
                        })
            
            return overdue_borrows
        except Exception as e:
            logger.error(f"Gecikmiş bildirim hatası: {str(e)}")
            return []

    @staticmethod
    def get_upcoming_due_notifications(user_id, days_ahead=3):
        """Yaklaşan son tarih bildirimleri"""
        try:
            now = datetime.now(timezone.utc)
            future_date = now + timedelta(days=days_ahead)
            
            borrows = Borrow.query.filter_by(
                user_id=user_id,
                return_date=None
            ).all()
            
            upcoming = []
            for borrow in borrows:
                if borrow.due_date:
                    due_date = borrow.due_date
                    if due_date.tzinfo is None:
                        due_date = due_date.replace(tzinfo=timezone.utc)
                    
                    if now < due_date <= future_date:
                        days_left = (due_date - now).days
                        upcoming.append({
                            'borrow': borrow,
                            'days_left': days_left,
                            'book_name': borrow.book.name if borrow.book else 'Bilinmeyen'
                        })
            
            return upcoming
        except Exception as e:
            logger.error(f"Yaklaşan bildirim hatası: {str(e)}")
            return []

    @staticmethod
    def get_user_notifications(user_id):
        """Kullanıcı için tüm bildirimler"""
        overdue = NotificationService.get_overdue_notifications(user_id)
        upcoming = NotificationService.get_upcoming_due_notifications(user_id)
        
        return {
            'overdue': overdue,
            'upcoming': upcoming,
            'total': len(overdue) + len(upcoming)
        }

