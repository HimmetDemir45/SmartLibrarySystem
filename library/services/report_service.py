from library import db
from library.models import Borrow, Book, User, Category
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class ReportService:
    """Rapor oluşturma servisi"""

    @staticmethod
    def generate_monthly_report(year=None, month=None):
        """Aylık ödünç alma raporu"""
        try:
            if not year or not month:
                now = datetime.now(timezone.utc)
                year = now.year
                month = now.month
            
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
            borrows = Borrow.query.filter(
                Borrow.borrow_date >= start_date,
                Borrow.borrow_date < end_date
            ).all()
            
            total_borrows = len(borrows)
            total_returns = len([b for b in borrows if b.return_date])
            total_fines = sum([b.fine_amount or 0 for b in borrows])
            
            # En çok ödünç alınan kitaplar
            popular_books = db.session.query(
                Book,
                func.count(Borrow.id).label('count')
            ).join(Borrow, Borrow.book_id == Book.id)\
             .filter(Borrow.borrow_date >= start_date, Borrow.borrow_date < end_date)\
             .group_by(Book.id)\
             .order_by(func.count(Borrow.id).desc())\
             .limit(5).all()
            
            return {
                'period': f"{year}-{month:02d}",
                'total_borrows': total_borrows,
                'total_returns': total_returns,
                'total_fines': float(total_fines),
                'popular_books': [{'book': book, 'count': count} for book, count in popular_books]
            }
        except Exception as e:
            logger.error(f"Aylık rapor hatası: {str(e)}")
            return None

    @staticmethod
    def generate_user_report(user_id):
        """Kullanıcı özel raporu"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            borrows = Borrow.query.filter_by(user_id=user_id).all()
            total_borrows = len(borrows)
            active_borrows = len([b for b in borrows if not b.return_date])
            total_fines = sum([b.fine_amount or 0 for b in borrows])
            
            # En çok okunan kategoriler
            category_stats = db.session.query(
                Category.name,
                func.count(Borrow.id).label('count')
            ).join(Book, Borrow.book_id == Book.id)\
             .join(Category, Book.category_id == Category.id)\
             .filter_by(user_id=user_id)\
             .group_by(Category.id)\
             .order_by(func.count(Borrow.id).desc())\
             .limit(5).all()
            
            return {
                'user': user,
                'total_borrows': total_borrows,
                'active_borrows': active_borrows,
                'total_fines': float(total_fines),
                'favorite_categories': [{'name': name, 'count': count} for name, count in category_stats]
            }
        except Exception as e:
            logger.error(f"Kullanıcı raporu hatası: {str(e)}")
            return None

