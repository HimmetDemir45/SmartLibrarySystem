from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from library.models import User, Book, Borrow
from library.services.loan_service import LoanService

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home_page():
    return render_template('home.html')

@main_bp.route('/profile')
@login_required
def profile_page():
    # ADMIN İSE: İstatistikleri göster
    if current_user.is_admin:
        total_users = User.query.count()
        total_books = Book.query.count()
        active_loans = Borrow.query.filter_by(return_date=None).count()
        # Kendisi hariç diğer üyeler
        users = User.query.filter(User.id != current_user.id).all()

        return render_template('profile.html',
                               total_users=total_users,
                               total_books=total_books,
                               active_loans=active_loans,
                               users=users)

    # NORMAL KULLANICI İSE: Kendi geçmişini göster
    else:
        my_history = LoanService.get_user_history(current_user.id)
        total_fine = LoanService.calculate_total_fine(current_user.id)
        return render_template('profile.html', history=my_history, total_fine=total_fine)

@main_bp.route('/forgive/<int:user_id>')
@login_required
def forgive_user_fine(user_id):
    if not current_user.is_admin:
        flash("Yetkiniz yok!", category='danger')
        return redirect(url_for('main_bp.profile_page'))

    success = LoanService.forgive_fines(user_id)
    if success:
        flash(f"Kullanıcının cezaları silindi (Af uygulandı).", category='success')
    else:
        flash("Bir hata oluştu.", category='danger')

    return redirect(url_for('main_bp.profile_page'))