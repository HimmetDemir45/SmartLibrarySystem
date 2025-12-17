from flask import Blueprint, render_template
from flask_login import login_required, current_user
from library.services.book_service import BookService
from library.services.loan_service import LoanService

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home_page():
    latest_books_pagination = BookService.get_all_paginated(page=1, per_page=4)
    return render_template('home.html', latest_books=latest_books_pagination.items)

@main_bp.route('/profile')
@login_required # <-- Giriş zorunluluğu eklendi
def profile_page():
    # Kullanıcının aktif kitapları (zaten current_user üzerinden veya servisten alınabilir)
    active_loans = LoanService.get_user_active_loans(current_user.id)

    # Kullanıcının geçmiş hareketleri (İade ettikleri dahil)
    history = LoanService.get_user_history(current_user.id)

    return render_template('profile.html', active_loans=active_loans, history=history)