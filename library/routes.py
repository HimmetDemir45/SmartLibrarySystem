from library import app, db
from flask import render_template, redirect, url_for, flash, request
from library.models import Book, User, Borrow
from library.forms import RegisterForm, LoginForm, BorrowBookForm, ReturnBookForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/library', methods=['GET', 'POST'])
@login_required
def library_page():
    borrow_form = BorrowBookForm()
    return_form = ReturnBookForm()

    if request.method == "POST":
        # --- ÖDÜNÇ ALMA (BORROW) ---
        borrowed_book_name = request.form.get('borrowed_book_name')
        if borrowed_book_name: # Hangi formun geldiğini anlamak için basit kontrol
            book_to_borrow = Book.query.filter_by(name=borrowed_book_name).first()
            if book_to_borrow and book_to_borrow.is_available:
                book_to_borrow.is_available = False
                due_date = datetime.utcnow() + timedelta(days=15)
                borrow_record = Borrow(user_id=current_user.id, book_id=book_to_borrow.id, due_date=due_date)
                db.session.add(borrow_record)
                db.session.commit()
                flash(f"Tebrikler! {book_to_borrow.name} kitabını ödünç aldınız.", category='success')
            else:
                flash(f"Bu kitap şu an müsait değil.", category='danger')

        # --- İADE ETME (RETURN) - TRIGGER DEVREDE ---
        returned_book_name = request.form.get('returned_book_name')
        if returned_book_name:
            book_to_return = Book.query.filter_by(name=returned_book_name).first()
            if book_to_return:
                active_borrow = Borrow.query.filter_by(user_id=current_user.id, book_id=book_to_return.id, return_date=None).first()
                if active_borrow:
                    # 1. Sadece tarihi güncelle
                    active_borrow.return_date = datetime.utcnow()

                    # 2. Kitabı müsait yap
                    book_to_return.is_available = True

                    # 3. Kaydet (Burada SQL Trigger otomatik çalışacak ve cezayı hesaplayacak)
                    db.session.commit()

                    flash(f"{book_to_return.name} iade edildi. Ceza varsa sistem otomatik hesapladı.", category='success')
                else:
                    flash(f"İade edilecek kayıt bulunamadı.", category='danger')

        return redirect(url_for('library_page'))

    if request.method == "GET":
        books = Book.query.all()
        current_borrows = Borrow.query.filter_by(user_id=current_user.id, return_date=None).all()
        owned_books = [borrow.book for borrow in current_borrows]
        return render_template('library.html', items=books, purchase_form=borrow_form, owned_items=owned_books, selling_form=return_form)
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Hesap oluşturuldu! Giriş yapıldı: {user_to_create.username}", category='success')
        return redirect(url_for('library_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Hata oluştu: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Başarılı! Giriş yaptınız: {attempted_user.username}', category='success')
            return redirect(url_for('library_page'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("Çıkış yaptınız!", category='info')
    return redirect(url_for("home_page"))