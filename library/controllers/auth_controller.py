from flask import Blueprint, render_template, redirect, url_for, flash, request
from library.forms import RegisterForm, LoginForm
from library.models import User
from library.services.auth_service import AuthService
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        # AuthService kullanarak login kontrolü yap
        attempted_user = AuthService.check_user_login(
            username=form.username.data,
            password=form.password.data
        )

        if attempted_user:
            # Admin değilse ve onayı yoksa giriş yapmasına izin verme
            if not attempted_user.is_admin and not attempted_user.is_approved:
                flash('⚠️ Hesabınız henüz onaylanmamış. Lütfen yönetici onayı bekleyin.', category='warning')
                return render_template('login.html', form=form)
            
            login_user(attempted_user)
            flash(f'Başarıyla giriş yaptınız: {attempted_user.username}', category='success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('book_bp.library_page'))
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