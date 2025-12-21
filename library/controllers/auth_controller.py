from flask import Blueprint, render_template, redirect, url_for, flash, request
from library.forms import RegisterForm, LoginForm
from library.models import User
from library.services.auth_service import AuthService
from flask_login import login_user, logout_user
from library.middleware.rate_limiter import RateLimiter

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    
    # Rate limiting kontrolü (Brute Force koruması)
    client_ip = RateLimiter.get_client_ip()
    username = form.username.data if form.is_submitted() else None
    
    # IP ve kullanıcı adı kombinasyonu için rate limit
    rate_limit_key = f"{client_ip}:{username}" if username else client_ip
    
    if RateLimiter.is_rate_limited(rate_limit_key, max_attempts=5, window_seconds=300):
        flash('⚠️ Çok fazla başarısız giriş denemesi yaptınız. Lütfen 5 dakika sonra tekrar deneyin.', category='danger')
        return render_template('login.html', form=form)
    
    if form.validate_on_submit():
        # AuthService kullanarak login kontrolü yap
        attempted_user = AuthService.check_user_login(
            username=form.username.data,
            password=form.password.data
        )

        if attempted_user:
            # Başarılı giriş - rate limit'i sıfırla
            RateLimiter.reset_rate_limit(rate_limit_key)
            
            # Admin değilse ve onayı yoksa giriş yapmasına izin verme
            if not attempted_user.is_admin and not attempted_user.is_approved:
                flash('⚠️ Hesabınız henüz onaylanmamış. Lütfen yönetici onayı bekleyin.', category='warning')
                return render_template('login.html', form=form)
            
            # Session Fixation koruması: Login öncesi session'ı temizle
            from flask import session
            session.clear()
            
            # Yeni session ile login yap
            login_user(attempted_user, remember=False)
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