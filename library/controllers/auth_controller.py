from flask import Blueprint, render_template, redirect, url_for, flash, request
from library.forms import RegisterForm, LoginForm, RequestResetForm, ResetPasswordForm
from library.services.auth_service import AuthService
from flask_login import login_user, logout_user, current_user
from library.middleware.rate_limiter import RateLimiter
from library.models.user import User
from library import db, bcrypt
from library import mail  # __init__.py'de tanımladığımız mail objesi
from flask_mail import Message
auth_bp = Blueprint('auth_bp', __name__)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Parola Sıfırlama İsteği - Akıllı Kütüphane',
                  sender='noreply@kutuphane.com',
                  recipients=[user.email_address])

    msg.body = f'''Parolanızı sıfırlamak için aşağıdaki linke tıklayın:
{url_for('auth_bp.reset_token', token=token, _external=True)}

Eğer bu isteği siz yapmadıysanız, bu mesajı görmezden gelin; hiçbir değişiklik yapılmayacaktır.
'''
    mail.send(msg)
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

  # Yeni formları import et

# --- ŞİFRE SIFIRLAMA İSTEĞİ (E-posta girilen sayfa) ---
@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('book_bp.library_page'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email.data).first()

        # --- DEĞİŞEN KISIM BAŞLANGIÇ ---
        if user:
            send_reset_email(user) # Artık gerçekten e-posta atıyor!
        # --- DEĞİŞEN KISIM BİTİŞ ---

        flash('Şifre sıfırlama talimatları e-posta adresinize gönderildi.', 'info')
        return redirect(url_for('auth_bp.login_page'))

    return render_template('reset_request.html', title='Şifremi Unuttum', form=form)

# --- ŞİFRE SIFIRLAMA (Yeni şifre belirlenen sayfa) ---
@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('book_bp.library_page'))

    # Token doğrulama işlemi User modelinde yapılmalı
    user = User.verify_reset_token(token)
    if user is None:
        flash('Bu link geçersiz veya süresi dolmuş.', 'warning')
        return redirect(url_for('auth_bp.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Yeni şifreyi kaydet (AuthService veya direkt burada)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()

        flash('Şifreniz başarıyla güncellendi! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth_bp.login_page'))

    return render_template('reset_token.html', title='Şifreyi Sıfırla', form=form)