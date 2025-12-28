from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from library.forms import AddAuthorForm, AddCategoryForm, AddBookForm
from library.services.author_service import AuthorService
from library.services.category_service import CategoryService
from library.services.book_service import BookService
from library.services.loan_service import LoanService
from library.services.file_service import FileService
from library.services.stats_service import StatsService
from library.services.report_service import ReportService
from library.repositories.user_repository import UserRepository
from library import db
from sqlalchemy import func
from library.models.book import Book
from library.models.category import Category
import logging

# Hata ayıklama için logger
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_bp', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Giriş yapmalısınız.", category='danger')
            return redirect(url_for('auth_bp.login_page'))
        if not current_user.is_admin:
            flash("Bu sayfaya erişim yetkiniz yok.", category='danger')
            # 403 Forbidden döndür
            from flask import abort
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_required
def admin_page():
    # Formları oluştur
    author_form = AddAuthorForm()
    category_form = AddCategoryForm()
    add_book_form = AddBookForm()

    # --- POST İŞLEMLERİ ---
    if request.method == 'POST':
        # 1. KİTAP EKLEME
        if 'book_submit' in request.form and add_book_form.validate_on_submit():
            try:
                image_file_name = 'default.jpg'
                if add_book_form.image.data:
                    image_file_name = FileService.save_picture(add_book_form.image.data)

                BookService.add_book(
                    name=add_book_form.name.data,
                    author=add_book_form.author.data,
                    category=add_book_form.category.data,
                    barcode=add_book_form.barcode.data,
                    description=add_book_form.description.data,
                    image_file=image_file_name
                )
                flash(f"'{add_book_form.name.data}' kütüphaneye eklendi!", 'success')
                return redirect(url_for('admin_bp.admin_page'))
            except Exception as e:
                flash(f"Kitap eklenirken hata: {str(e)}", 'danger')

        # 2. YAZAR EKLEME
        elif 'author_submit' in request.form and author_form.validate_on_submit():
            try:
                AuthorService.add_author(author_form.name.data)
                flash(f"Yazar '{author_form.name.data}' başarıyla eklendi.", 'success')
                return redirect(url_for('admin_bp.admin_page'))
            except Exception as e:
                flash(f"Yazar ekleme hatası: {str(e)}", 'danger')

        # 3. KATEGORİ EKLEME
        elif 'category_submit' in request.form and category_form.validate_on_submit():
            try:
                CategoryService.add_category(category_form.name.data)
                flash(f"Kategori '{category_form.name.data}' başarıyla eklendi.", 'success')
                return redirect(url_for('admin_bp.admin_page'))
            except Exception as e:
                flash(f"Kategori ekleme hatası: {str(e)}", 'danger')

        # Form validasyon hataları varsa göster
        if add_book_form.errors:
            for field, errors in add_book_form.errors.items():
                for error in errors:
                    flash(f"Kitap formu hatası ({field}): {error}", "danger")

    # --- VERİ ÇEKME İŞLEMLERİ (GET) ---
    try:
        authors = AuthorService.get_all_authors()
        categories = CategoryService.get_all_categories()
        user_repo = UserRepository()
        all_users = user_repo.get_all()
        active_loans = LoanService.get_all_active_loans_with_fine()
    except Exception as e:
        logger.error(f"Temel veri çekme hatası: {e}")
        flash("Veriler yüklenirken bir sorun oluştu.", "warning")
        authors, categories, all_users, active_loans = [], [], [], []

    # --- GRAFİK VERİLERİ ---
    cat_labels = []
    cat_values = []
    try:
        # Tuple unpack hatasını önlemek için güvenli sorgu
        cat_stats = db.session.query(Category.name, func.count(Book.id)) \
            .outerjoin(Book, Book.category_id == Category.id) \
            .group_by(Category.id).all()

        # Liste comprehension ile verileri ayır (burası güvenlidir çünkü sorgu 2 alan döner)
        if cat_stats:
            cat_labels = [stat[0] for stat in cat_stats]
            cat_values = [stat[1] for stat in cat_stats]

    except Exception as e:
        logger.error(f"Grafik verisi hatası: {e}")
        # Hata olsa bile sayfa açılsın diye boş bırakıyoruz

    # --- İSTATİSTİKLER VE RAPOR ---
    library_stats = None
    monthly_report = None
    try:
        library_stats = StatsService.get_library_stats()
        monthly_report = ReportService.generate_monthly_report()
    except ValueError as ve:
        # Hatanın asıl kaynağı muhtemelen servislerin içindeki bir döngüde
        logger.error(f"İstatistik servisi unpack hatası: {ve}")
        flash("İstatistikler hesaplanırken bir veri uyumsuzluğu oluştu.", "warning")
    except Exception as e:
        logger.error(f"Rapor servisi hatası: {e}")

    return render_template('admin_dashboard.html',
                           author_form=author_form,
                           category_form=category_form,
                           add_book_form=add_book_form,
                           authors=authors,
                           categories=categories,
                           all_users=all_users,
                           active_loans=active_loans,
                           cat_labels=cat_labels,
                           cat_values=cat_values,
                           library_stats=library_stats,
                           monthly_report=monthly_report)


@admin_bp.route('/admin/update_author/<int:author_id>', methods=['POST'])
@admin_required
def update_author(author_id):
    new_name = request.form.get('name')
    if new_name:
        try:
            if AuthorService.update_author(author_id, new_name):
                flash(f"Yazar güncellendi.", 'success')
            else:
                flash("Yazar güncellenemedi.", 'danger')
        except Exception as e:
            flash(f"Hata: {str(e)}", 'danger')
    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    try:
        if CategoryService.delete_category(category_id):
            flash("Kategori silindi.", 'success')
        else:
            flash("Kategori silinemedi.", 'danger')
    except Exception as e:
        flash(f"Hata: {str(e)}", 'danger')
    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/forgive_fines/<int:user_id>', methods=['POST'])
@admin_required
def forgive_fines(user_id):
    if LoanService.forgive_fines(user_id):
        flash(f"Kullanıcının cezaları affedildi.", 'success')
    else:
        flash(f"İşlem başarısız.", 'danger')
    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/update_book/<int:book_id>', methods=['POST'])
@admin_required
def update_book(book_id):
    try:
        update_data = {
            'name': request.form.get('name'),
            'author': request.form.get('author'),
            'category': request.form.get('category'),
            'barcode': request.form.get('barcode'),
            'description': request.form.get('description')
        }
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                update_data['image_file'] = FileService.save_picture(file)

        BookService.update_book(book_id, update_data)
        flash("Kitap güncellendi.", 'success')
    except Exception as e:
        flash(f"Hata: {e}", 'danger')
    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/delete_book/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    try:
        if BookService.delete_book(book_id):
            flash("Kitap silindi.", 'success')
        else:
            flash("Kitap silinemedi (Ödünçte olabilir).", 'danger')
    except Exception as e:
        flash(f"Hata: {e}", 'danger')
    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@admin_required
def approve_user(user_id):
    repo = UserRepository()
    user = repo.get_by_id(user_id)
    if user:
        user.is_approved = True
        db.session.commit()
        flash(f"{user.username} onaylandı.", "success")
    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/update_budget/<int:user_id>', methods=['POST'])
@admin_required
def update_budget(user_id):
    """
    Kullanıcı bakiyesini günceller (ekle/çıkar/belirle).
    Güvenlik: Admin kontrolü, negatif değer kontrolü, tip kontrolü
    """
    try:
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)

        if not user:
            flash("Kullanıcı bulunamadı.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        operation = request.form.get('operation')
        amount_str = request.form.get('amount', '0')

        # Tip kontrolü ve validasyon - Daha sıkı kontrol
        if not amount_str or amount_str.strip() == '':
            flash("Miktar boş olamaz.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        # String kontrolü - sadece sayısal karakterler
        if not amount_str.replace('.', '').replace('-', '').isdigit():
            flash("Geçersiz miktar değeri. Sadece sayısal değer kabul edilir.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            flash("Geçersiz miktar değeri.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        # Negatif değer kontrolü - İşlemden önce kontrol et
        if amount < 0:
            flash("Miktar negatif olamaz.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        # NaN ve Infinity kontrolü
        import math
        if math.isnan(amount) or math.isinf(amount):
            flash("Geçersiz miktar değeri.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        # Maksimum değer kontrolü (güvenlik için)
        MAX_BUDGET = 100000  # 100000 TL maksimum
        if amount > MAX_BUDGET:
            flash(f"Maksimum bakiye limiti aşıldı (Max: {MAX_BUDGET} TL)", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        old_budget = user.budget

        if operation == 'add':
            new_budget = user.budget + amount
            if new_budget > MAX_BUDGET:
                flash(f"Toplam bakiye maksimum limiti aşamaz (Max: {MAX_BUDGET} TL)", "danger")
                return redirect(url_for('admin_bp.admin_page'))
            user.budget = new_budget
            flash(f"'{user.username}' bakiyesine {amount} TL eklendi. Yeni bakiye: {user.budget} TL", "success")
        elif operation == 'subtract':
            if user.budget < amount:
                flash(f"Yetersiz bakiye! Mevcut: {user.budget} TL, Çıkarılacak: {amount} TL", "danger")
                return redirect(url_for('admin_bp.admin_page'))
            user.budget -= amount
            flash(f"'{user.username}' bakiyesinden {amount} TL çıkarıldı. Yeni bakiye: {user.budget} TL", "success")
        elif operation == 'set':
            user.budget = amount
            flash(f"'{user.username}' bakiyesi {amount} TL olarak ayarlandı.", "success")
        else:
            flash("Geçersiz işlem türü.", "danger")
            return redirect(url_for('admin_bp.admin_page'))

        db.session.commit()
        logger.info(
            f"Bakiye güncellendi: user_id={user_id}, operation={operation}, amount={amount}, old={old_budget}, new={user.budget}")
        return redirect(url_for('admin_bp.admin_page'))

    except ValueError:
        flash("Geçersiz miktar değeri.", "danger")
        return redirect(url_for('admin_bp.admin_page'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bakiye güncelleme hatası: {str(e)}")
        flash(f"Bakiye güncelleme hatası: {str(e)}", "danger")
        return redirect(url_for('admin_bp.admin_page'))
