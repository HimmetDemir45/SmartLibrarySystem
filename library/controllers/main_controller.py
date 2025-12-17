from flask import Blueprint, render_template
from flask_login import login_required, current_user
from library.services.book_service import BookService
from library.services.loan_service import LoanService
from library.services.stats_service import StatsService
from library.services.notification_service import NotificationService

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home_page():
    latest_books_pagination = BookService.get_all_paginated(page=1, per_page=4)
    # Popüler kitapları göster
    popular_books = StatsService.get_popular_books(limit=8)
    return render_template('home.html', 
                           latest_books=latest_books_pagination.items,
                           popular_books=popular_books)

@main_bp.route('/profile')
@login_required
def profile_page():
    # Kullanıcının şu an elinde olan kitapları getir
    active_books = LoanService.get_user_active_loans(current_user.id)

    # Kullanıcının geçmişteki tüm işlemlerinden kalan toplam cezasını hesapla
    total_fine = LoanService.calculate_total_fine(current_user.id)
    
    # Kullanıcı istatistiklerini getir
    user_stats = StatsService.get_user_stats(current_user.id)
    
    # Bildirimleri getir
    notifications = NotificationService.get_user_notifications(current_user.id)

    return render_template('profile.html',
                           active_books=active_books,
                           total_fine=total_fine,
                           user_stats=user_stats,
                           notifications=notifications)