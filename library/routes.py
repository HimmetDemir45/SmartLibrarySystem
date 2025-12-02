from library import app, db
from flask import render_template, redirect, url_for, flash, request
from library.models import Book, User, Borrow, Author, Category
from library.forms import RegisterForm, LoginForm, BorrowBookForm, ReturnBookForm, AddBookForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy import text
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/library', methods=['GET', 'POST'])
@login_required
def library_page():
    borrow_form = BorrowBookForm()
    return_form = ReturnBookForm()
    add_book_form = AddBookForm() # Yeni formumuz

    if request.method == "POST":
        # --- 1. KİTAP EKLEME (Sadece Admin) ---
        if add_book_form.validate_on_submit():
            # Yazar kontrolü (Varsa al, yoksa yarat)
            author_name = add_book_form.author.data
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.commit()

            # Kategori kontrolü
            category_name = add_book_form.category.data
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()

            # Kitabı oluştur
            new_book = Book(
                name=add_book_form.name.data,
                barcode=add_book_form.barcode.data,
                description=add_book_form.description.data,
                author_id=author.id,
                category_id=category.id,
                is_available=True
            )
            db.session.add(new_book)
            db.session.commit()
            flash(f"{new_book.name} başarıyla kütüphaneye eklendi!", category='success')
            return redirect(url_for('library_page'))

        # --- 2. ÖDÜNÇ ALMA ---
        borrowed_book_name = request.form.get('borrowed_book_name')
        if borrowed_book_name:
            book_to_borrow = Book.query.filter_by(name=borrowed_book_name).first()
            if book_to_borrow and book_to_borrow.is_available:
                book_to_borrow.is_available = False
                due_date = datetime.utcnow() + timedelta(days=15)
                borrow_record = Borrow(user_id=current_user.id, book_id=book_to_borrow.id, due_date=due_date)
                db.session.add(borrow_record)
                db.session.commit()
                flash(f"Tebrikler! {book_to_borrow.name} ödünç alındı.", category='success')
            else:
                flash(f"Bu kitap şu an müsait değil.", category='danger')

        # --- 3. İADE ETME ---
        returned_book_name = request.form.get('returned_book_name')
        if returned_book_name:
            book_to_return = Book.query.filter_by(name=returned_book_name).first()
            if book_to_return:
                active_borrow = Borrow.query.filter_by(user_id=current_user.id, book_id=book_to_return.id, return_date=None).first()
                if active_borrow:
                    active_borrow.return_date = datetime.utcnow()
                    book_to_return.is_available = True
                    db.session.commit()
                    flash(f"{book_to_return.name} iade edildi.", category='success')

        return redirect(url_for('library_page'))

    if request.method == "GET":
        # --- ARAMA MANTIĞI BURAYA EKLENDİ ---
        search_query = request.args.get('q') # URL'den 'q' parametresini al (Örn: ?q=Harry)

        if search_query:
            # Hem Kitap Adında, hem Yazar Adında, hem de Kategoride arama yap (Müthiş Özellik)
            books = Book.query.join(Author).join(Category).filter(
                (Book.name.contains(search_query)) |
                (Author.name.contains(search_query)) |
                (Category.name.contains(search_query)) |
                (Book.barcode.contains(search_query))
            ).all()
            if not books:
                flash("Aradığınız kriterlere uygun kitap bulunamadı.", category='warning')
        else:
            # Arama yoksa hepsini getir
            books = Book.query.all()

        current_borrows = Borrow.query.filter_by(user_id=current_user.id, return_date=None).all()
        owned_books = [borrow.book for borrow in current_borrows]

        return render_template('library.html', items=books, purchase_form=borrow_form,
                               owned_items=owned_books, selling_form=return_form,
                               add_book_form=add_book_form)
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

# ==========================================
# API ENDPOINTS (Hocanın İstediği Profesyonel Yapı)
# ==========================================

# 1. TÜM KİTAPLARI GETİR (GET)
@app.route('/api/books', methods=['GET'])
def get_all_books_api():
    try:
        books = Book.query.all()
        output = []
        for book in books:
            book_data = {
                'id': book.id,
                'name': book.name,
                'barcode': book.barcode,
                'description': book.description,
                'author': book.author.name,
                'category': book.category.name,
                'is_available': book.is_available
            }
            output.append(book_data)

        # STANDART CEVAP: success + message + data
        return jsonify({
            'success': True,
            'message': 'Kitap listesi başarıyla çekildi.',
            'data': output
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {str(e)}',
            'data': None
        }), 500

# 2. TEK KİTAP GETİR (GET)
@app.route('/api/book/<int:id>', methods=['GET'])
def get_single_book_api(id):
    book = Book.query.get(id)

    if book:
        book_data = {
            'id': book.id,
            'name': book.name,
            'barcode': book.barcode,
            'author': book.author.name,
            'is_available': book.is_available
        }
        return jsonify({
            'success': True,
            'message': 'Kitap detaylari bulundu.',
            'data': book_data
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Aradiginiz ID ile eslesen kitap bulunamadı.',
            'data': None
        }), 404

# 3. KİTAP ÖDÜNÇ AL (POST) - API Versiyonu
@app.route('/api/borrow', methods=['POST'])
def borrow_book_api():
    # Postman'den gelen veriyi al (x-www-form-urlencoded veya json)
    book_name = request.form.get('book_name')

    # Kullanıcı giriş yapmış mı kontrolü (Basit API simülasyonu için kapalı tutulabilir ama doğrusu budur)
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Lütfen önce giriş yapınız.'}), 401

    if not book_name:
        return jsonify({'success': False, 'message': 'Kitap ismi gönderilmedi.'}), 400

    book = Book.query.filter_by(name=book_name).first()

    if book:
        if book.is_available:
            # İşlemleri yap
            book.is_available = False
            due_date = datetime.utcnow() + timedelta(days=15)
            borrow_record = Borrow(user_id=current_user.id, book_id=book.id, due_date=due_date)
            db.session.add(borrow_record)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'{book.name} basariyla odunc alindi.',
                'data': {
                    'book': book.name,
                    'due_date': due_date.strftime('%Y-%m-%d')
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Bu kitap su an baskasinda.'}), 400
    else:
        return jsonify({'success': False, 'message': 'Kitap bulunamadı.'}), 404

# 4. KİTAP İADE ET (POST) - API Versiyonu
@app.route('/api/return', methods=['POST'])
def return_book_api():
    book_name = request.form.get('book_name')

    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Lütfen önce giriş yapınız.'}), 401

    book = Book.query.filter_by(name=book_name).first()

    if book:
        active_borrow = Borrow.query.filter_by(user_id=current_user.id, book_id=book.id, return_date=None).first()
        if active_borrow:
            active_borrow.return_date = datetime.utcnow()
            book.is_available = True
            db.session.commit() # Trigger burada çalışacak

            return jsonify({
                'success': True,
                'message': f'{book.name} iade edildi. Tesekkurler.',
                'data': None
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Bu kitap sizde gorunmuyor.'}), 400
    else:
        return jsonify({'success': False, 'message': 'Kitap bulunamadi.'}), 404

# 5. KİTAP BİLGİLERİNİ GÜNCELLE (PUT) - Örn: Açıklamayı değiştir
@app.route('/api/book/<int:id>', methods=['PUT'])
def update_book_api(id):
    # Kullanıcı giriş yapmış mı ve Admin mi? (Basitlik için sadece giriş kontrolü yapıyoruz)
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 401

    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'message': 'Kitap bulunamadı.'}), 404

    # Postman'den gelen yeni verileri al
    # PUT isteklerinde veriler genellikle 'form' değil 'json' olarak gelir ama form da destekleyelim
    new_description = request.form.get('description')

    if new_description:
        book.description = new_description
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{book.name} kitabı başarıyla güncellendi.',
            'data': {
                'id': book.id,
                'new_description': book.description
            }
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Değiştirilecek veri gönderilmedi.'}), 400

# 6. KİTAP SİL (DELETE)
@app.route('/api/book/<int:id>', methods=['DELETE'])
def delete_book_api(id):
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 401

    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'message': 'Kitap bulunamadı.'}), 404

    try:
        # Önce bu kitaba ait borç kayıtlarını (Foreign Key) temizlemek gerekebilir
        # Ama şimdilik doğrudan kitabı silmeyi deneyelim
        db.session.delete(book)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{book.name} kütüphaneden kalıcı olarak silindi.',
            'data': None
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Silinemedi. Kitap kullanımda olabilir: {str(e)}'}), 500

# --- WEB ARAYÜZÜ İÇİN SİLME İŞLEMİ ---
@app.route('/delete_book_web/<int:id>')
@login_required
def delete_book_web(id):
    # Sadece Admin silebilir
    if not current_user.is_admin:
        flash("Bu işlem için yetkiniz yok!", category='danger')
        return redirect(url_for('library_page'))

    book = Book.query.get(id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
            flash(f"{book.name} kitabı başarıyla silindi.", category='success')
        except:
            flash("Kitap silinemedi. Şu an birinde ödünçte olabilir.", category='danger')

    return redirect(url_for('library_page'))

# --- KİTAP DÜZENLEME (UPDATE) ---
@app.route('/edit_book_web/<int:id>', methods=['POST'])
@login_required
def edit_book_web(id):
    # 1. Yetki Kontrolü
    if not current_user.is_admin:
        flash("Bu işlem için yetkiniz yok!", category='danger')
        return redirect(url_for('library_page'))

    # 2. Kitabı Bul
    book = Book.query.get(id)
    if not book:
        flash("Kitap bulunamadı.", category='danger')
        return redirect(url_for('library_page'))

    # 3. Formdan Gelen Yeni Verileri Al
    new_name = request.form.get('name')
    new_author_name = request.form.get('author')
    new_category_name = request.form.get('category')
    new_barcode = request.form.get('barcode')
    new_description = request.form.get('description')

    if request.method == "POST":
        try:
            # Yazar Değiştiyse Kontrol Et (Varsa bul, yoksa yarat)
            author = Author.query.filter_by(name=new_author_name).first()
            if not author:
                author = Author(name=new_author_name)
                db.session.add(author)
                db.session.commit()

            # Kategori Değiştiyse Kontrol Et
            category = Category.query.filter_by(name=new_category_name).first()
            if not category:
                category = Category(name=new_category_name)
                db.session.add(category)
                db.session.commit()

            # Kitap Bilgilerini Güncelle
            book.name = new_name
            book.barcode = new_barcode
            book.description = new_description
            book.author_id = author.id      # Yeni yazar ID'si
            book.category_id = category.id  # Yeni kategori ID'si

            db.session.commit()
            flash(f"{book.name} bilgileri güncellendi.", category='success')

        except Exception as e:
            flash(f"Güncelleme sırasında hata oluştu: {str(e)}", category='danger')

    return redirect(url_for('library_page'))
# En üste eklemeyi unutma: from sqlalchemy import text

# --- PROFİL SAYFASI ---
@app.route('/profile')
@login_required
def profile_page():
    # 1. KULLANICI ADMİN İSE: Patron ekranı verilerini hazırla
    if current_user.is_admin:
        # İstatistikler
        total_users = User.query.count()
        total_books = Book.query.count()
        # Aktif ödünç verilen kitap sayısı
        active_loans = Borrow.query.filter_by(return_date=None).count()

        # Ceza Yönetimi için Tüm Kullanıcıları Çek
        # (Kendisi hariç diğer kullanıcıları listele)
        users = User.query.filter(User.id != current_user.id).all()

        return render_template('profile.html',
                               total_users=total_users,
                               total_books=total_books,
                               active_loans=active_loans,
                               users=users)

    # 2. NORMAL KULLANICI İSE: Sadece kendi geçmişini hazırla
    else:
        # Kullanıcının tüm işlem geçmişi (Hem iade ettikleri hem elindekiler)
        my_history = Borrow.query.filter_by(user_id=current_user.id).order_by(Borrow.borrow_date.desc()).all()

        # Toplam Ceza Hesabı (Veritabanındaki fine_amount'ları topla)
        total_fine = 0
        for record in my_history:
            if record.fine_amount:
                total_fine += record.fine_amount

        return render_template('profile.html', history=my_history, total_fine=total_fine)

# --- CEZA AFFETME (STORED PROCEDURE KULLANIMI) ---
@app.route('/forgive/<int:user_id>')
@login_required
def forgive_user_fine(user_id):
    # Sadece Admin yapabilir
    if not current_user.is_admin:
        flash("Yetkiniz yok!", category='danger')
        return redirect(url_for('profile_page'))

    try:
        # --- BURADA STORED PROCEDURE ÇAĞIRIYORUZ ---
        # seed.py içinde tanımladığımız 'sp_ForgiveFines' prosedürünü çalıştır
        db.session.execute(text("CALL sp_ForgiveFines(:p_id)"), {'p_id': user_id})
        db.session.commit()

        user = User.query.get(user_id)
        flash(f"{user.username} kullanıcısının tüm cezaları silindi (Af uygulandı).", category='success')
    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", category='danger')

    return redirect(url_for('profile_page'))