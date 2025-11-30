from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Book, User, Borrow
from market.forms import RegisterForm, LoginForm, BorrowBookForm, ReturnBookForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/library', methods=['GET', 'POST'])
@login_required
def library_page():
    # Formları oluştur
    borrow_form = BorrowBookForm()
    return_form = ReturnBookForm()

    if request.method == "POST":
        # --- ÖDÜNÇ ALMA (BORROW) MANTIĞI ---
        # HTML'den gelen kitabın ismini veya ID'sini alacağız
        borrowed_book_name = request.form.get('borrowed_book_name')
        book_to_borrow = Book.query.filter_by(name=borrowed_book_name).first()

        if book_to_borrow:
            if book_to_borrow.is_available:
                # 1. Kitabın durumunu güncelle
                book_to_borrow.is_available = False

                # 2. Ödünç alma kaydı oluştur (Şu anki zaman ve 15 gün sonrası)
                due_date = datetime.utcnow() + timedelta(days=15)
                borrow_record = Borrow(user_id=current_user.id,
                                       book_id=book_to_borrow.id,
                                       due_date=due_date)

                # 3. Veritabanına kaydet
                db.session.add(borrow_record)
                db.session.commit()

                flash(f"Tebrikler! {book_to_borrow.name} kitabını ödünç aldınız. Son teslim tarihi: {due_date.strftime('%Y-%m-%d')}", category='success')
            else:
                flash(f"Üzgünüm, {book_to_borrow.name} kitabı şu an başkasında!", category='danger')

        # --- İADE ETME (RETURN) MANTIĞI ---
        returned_book_name = request.form.get('returned_book_name')
        book_to_return = Book.query.filter_by(name=returned_book_name).first()

        if book_to_return:
            # Kullanıcının bu kitaba ait aktif (henüz iade edilmemiş) kaydını bul
            active_borrow = Borrow.query.filter_by(user_id=current_user.id, book_id=book_to_return.id, return_date=None).first()

            if active_borrow:
                # 1. İade tarihini şimdiki zaman yap
                active_borrow.return_date = datetime.utcnow()

                # 2. Kitabı tekrar müsait yap
                book_to_return.is_available = True

                # 3. Ceza Hesabı (PDF Madde 6)
                # Eğer iade tarihi, teslim tarihinden (due_date) büyükse ceza kes
                if active_borrow.return_date > active_borrow.due_date:
                    delta = active_borrow.return_date - active_borrow.due_date
                    fine = delta.days * 5.0 # Günlük 5 TL/Dolar ceza
                    active_borrow.fine_amount = fine
                    flash(f"Kitabı geç getirdiniz! Ceza tutarı: {fine}", category='warning')
                else:
                    flash(f"Teşekkürler, {book_to_return.name} kitabını zamanında iade ettiniz.", category='success')

                db.session.commit()
            else:
                flash(f"Bu kitabı zaten iade etmişsiniz veya sizde görünmüyor.", category='danger')

        return redirect(url_for('library_page'))

    if request.method == "GET":
        # Sadece müsait olan kitapları ve kullanıcının elindeki kitapları ayırabiliriz
        books = Book.query.all()
        # Kullanıcının şu an elinde olan kitapları bulmak için Borrow tablosundan sorgu yapıyoruz
        # (return_date'i boş olan kayıtlar kullanıcının elindedir)
        current_borrows = Borrow.query.filter_by(user_id=current_user.id, return_date=None).all()
        owned_books = [borrow.book for borrow in current_borrows]

        return render_template('market.html', items=books, purchase_form=borrow_form, owned_items=owned_books, selling_form=return_form)

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