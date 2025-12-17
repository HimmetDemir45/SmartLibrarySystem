from library import db
from library.models import Book, Borrow, User, Category, Author
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

class StatsService:
    """Kütüphane istatistikleri için servis"""

    @staticmethod
    def get_library_stats():
        """Genel kütüphane istatistiklerini döndürür"""
        try:
            total_books = Book.query.count()
            available_books = Book.query.filter_by(is_available=True).count()
            borrowed_books = Book.query.filter_by(is_available=False).count()
            total_users = User.query.count()
            total_borrows = Borrow.query.count()
            active_borrows = Borrow.query.filter_by(return_date=None).count()
            
            # Kategorilere göre kitap sayıları
            category_stats = db.session.query(
                Category.name,
                func.count(Book.id).label('count')
            ).outerjoin(Book, Book.category_id == Category.id)\
             .group_by(Category.id)\
             .order_by(func.count(Book.id).desc())\
             .limit(5).all()
            
            # Yazarlara göre kitap sayıları
            author_stats = db.session.query(
                Author.name,
                func.count(Book.id).label('count')
            ).outerjoin(Book, Book.author_id == Author.id)\
             .group_by(Author.id)\
             .order_by(func.count(Book.id).desc())\
             .limit(5).all()
            
            # Son 30 gündeki ödünç alma sayısı
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_borrows = Borrow.query.filter(
                Borrow.borrow_date >= thirty_days_ago
            ).count()
            
            return {
                'total_books': total_books,
                'available_books': available_books,
                'borrowed_books': borrowed_books,
                'total_users': total_users,
                'total_borrows': total_borrows,
                'active_borrows': active_borrows,
                'recent_borrows': recent_borrows,
                'category_stats': [{'name': name, 'count': count} for name, count in category_stats],
                'author_stats': [{'name': name, 'count': count} for name, count in author_stats]
            }
        except Exception as e:
            logger.error(f"İstatistik hatası: {str(e)}")
            return None

    @staticmethod
    def get_user_stats(user_id):
        """Belirli bir kullanıcının istatistiklerini döndürür"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            total_borrows = Borrow.query.filter_by(user_id=user_id).count()
            active_borrows = Borrow.query.filter_by(user_id=user_id, return_date=None).count()
            
            # Toplam ceza
            total_fine = db.session.query(func.sum(Borrow.fine_amount))\
                .filter_by(user_id=user_id).scalar() or 0.0
            
            # En çok ödünç alınan kategoriler
            category_stats = db.session.query(
                Category.name,
                func.count(Borrow.id).label('count')
            ).join(Book, Borrow.book_id == Book.id)\
             .join(Category, Book.category_id == Category.id)\
             .filter_by(user_id=user_id)\
             .group_by(Category.id)\
             .order_by(func.count(Borrow.id).desc())\
             .limit(3).all()
            
            return {
                'username': user.username,
                'total_borrows': total_borrows,
                'active_borrows': active_borrows,
                'total_fine': float(total_fine),
                'favorite_categories': [{'name': name, 'count': count} for name, count in category_stats]
            }
        except Exception as e:
            logger.error(f"Kullanıcı istatistik hatası (user_id={user_id}): {str(e)}")
            return None

    @staticmethod
    def get_popular_books(limit=10):
        """En çok ödünç alınan kitapları döndürür"""
        try:
            popular_books = db.session.query(
                Book,
                func.count(Borrow.id).label('borrow_count')
            ).outerjoin(Borrow, Borrow.book_id == Book.id)\
             .group_by(Book.id)\
             .order_by(func.count(Borrow.id).desc())\
             .limit(limit).all()
            
            return [
                {
                    'book': book,
                    'borrow_count': count
                }
                for book, count in popular_books
            ]
        except Exception as e:
            logger.error(f"Popüler kitaplar hatası: {str(e)}")
            return []

