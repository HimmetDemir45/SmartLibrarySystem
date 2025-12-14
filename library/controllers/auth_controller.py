from flask import Blueprint, render_template, redirect, url_for, flash, request
from library.forms import RegisterForm, LoginForm
from library.services.auth_service import AuthService
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = AuthService.check_user_login(form.username.data, form.password.data)
        if user:
            login_user(user)
            flash(f'Giriş başarılı: {user.username}', category='success')
            return redirect(url_for('book_bp.library_page')) # Blueprint adına dikkat
        else:
            flash('Kullanıcı adı veya şifre hatalı!', category='danger')

    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = AuthService.register_user(
            username=form.username.data,
            email=form.email_address.data,
            password=form.password1.data
        )
        login_user(user)
        flash(f"Hesap oluşturuldu: {user.username}", category='success')
        return redirect(url_for('book_bp.library_page'))

    if form.errors:
        for err in form.errors.values():
            flash(f'Hata: {err}', category='danger')

    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout_page():
    logout_user()
    flash("Çıkış yaptınız!", category='info')
    return redirect(url_for("main_bp.home_page"))