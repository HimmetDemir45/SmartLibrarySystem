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
    # 1. Kullanıcının tüm ödünç geçmişini çek
    loan_history = LoanService.get_user_history(current_user.id)

    # 2. Toplam ceza miktarını hesapla
    total_fines = LoanService.calculate_total_fine(current_user.id)

    # 3. Profili render et
    return render_template('profile.html',
                           loan_history=loan_history, # <-- Yeni eklenen
                           total_fines=total_fines) # <-- Yeni eklenen

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