from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps  # (İsim çakışmasını önler)
from library.forms import AddAuthorForm, AddCategoryForm, AddBookForm
from library.services.author_service import AuthorService
from library.services.category_service import CategoryService
from library.services.book_service import BookService
from library.services.loan_service import LoanService
from library.services.file_service import FileService  # Resim kaydetmek için gerekli
from library.services.stats_service import StatsService  # İstatistikler için
from library.services.report_service import ReportService  # Raporlar için
from library.repositories.user_repository import UserRepository
from library import db
from sqlalchemy import func
from library.models.book import Book
from library.models.category import Category

admin_bp = Blueprint('admin_bp', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Bu sayfaya erişim yetkiniz yok.", category='danger')
            return redirect(url_for('main_bp.home_page'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_required
def admin_page():
    # Formları oluştur
    author_form = AddAuthorForm()
    category_form = AddCategoryForm()
    add_book_form = AddBookForm()  # --- Yeni Eklendi ---

    # Verileri çek
    authors = AuthorService.get_all_authors()
    categories = CategoryService.get_all_categories()
    user_repo = UserRepository()
    all_users = user_repo.get_all()
    active_loans = LoanService.get_all_active_loans_with_fine()

    if request.method == 'POST':
        # --- 1. KİTAP EKLEME İŞLEMİ (Buraya Taşındı) ---
        # 'book_submit' gizli inputunu kontrol ediyoruz (Hangi formun gönderildiğini anlamak için)
        if 'book_submit' in request.form and add_book_form.validate_on_submit():
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

        # --- 2. YAZAR EKLEME ---
        elif 'author_submit' in request.form and author_form.validate_on_submit():
            try:
                AuthorService.add_author(author_form.name.data)
                flash(f"Yazar '{author_form.name.data}' başarıyla eklendi.", 'success')
            except ValueError as e:
                flash(f"Yazar eklenemedi: {str(e)}", 'danger')
            except Exception as e:
                flash(f"Yazar eklenirken hata oluştu: {str(e)}", 'danger')
            return redirect(url_for('admin_bp.admin_page'))

        # --- 3. KATEGORİ EKLEME ---
        elif 'category_submit' in request.form and category_form.validate_on_submit():
            try:
                CategoryService.add_category(category_form.name.data)
                flash(f"Kategori '{category_form.name.data}' başarıyla eklendi.", 'success')
            except ValueError as e:
                flash(f"Kategori eklenemedi: {str(e)}", 'danger')
            except Exception as e:
                flash(f"Kategori eklenirken hata oluştu: {str(e)}", 'danger')
            return redirect(url_for('admin_bp.admin_page'))

    # Formda hata varsa (Validasyon hatası) kullanıcıya göster
    if add_book_form.errors:
        for err_msg in add_book_form.errors.values():
            flash(f"Kitap eklenirken hata: {err_msg}", "danger")
            # --- GRAFİK VERİLERİ ---
    # Kategorilere göre kitap sayılarını gruplayıp sayıyoruz
    # SQL Karşılığı: SELECT name, COUNT(book.id) FROM category JOIN book ... GROUP BY category.id
    cat_stats = db.session.query(Category.name, func.count(Book.id)) \
        .outerjoin(Book, Book.category_id == Category.id) \
        .group_by(Category.id).all()

    # Chart.js'in anlayacağı liste formatına çeviriyoruz
    cat_labels = [stat[0] for stat in cat_stats] # Örn: ['Roman', 'Bilim Kurgu']
    cat_values = [stat[1] for stat in cat_stats] # Örn: [15, 8]

    # İstatistikleri çek
    library_stats = StatsService.get_library_stats()
    
    # Aylık raporu çek
    monthly_report = ReportService.generate_monthly_report()

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

# --- DÜZENLEME ROTASI (Popup Modal ile yapılacak varsayılır) ---
@admin_bp.route('/admin/update_author/<int:author_id>', methods=['POST'])
@admin_required
def update_author(author_id):
    new_name = request.form.get('name')
    if not new_name:
        flash("İsim boş bırakılamaz.", 'danger')
        return redirect(url_for('admin_bp.admin_page'))

    try:
        success = AuthorService.update_author(author_id, new_name)
        if success:
            flash(f"Yazar (ID: {author_id}) başarıyla güncellendi.", 'success')
        else:
            flash("Yazar güncellenemedi veya bulunamadı.", 'danger')
    except ValueError as e:
        flash(f"Yazar güncellenemedi: {str(e)}", 'danger')
    except Exception as e:
        flash(f"Yazar güncellenirken hata oluştu: {str(e)}", 'danger')

    return redirect(url_for('admin_bp.admin_page'))


# --- SİLME ROTASI ---
@admin_bp.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    try:
        success = CategoryService.delete_category(category_id)
        if success:
            flash("Kategori başarıyla silindi.", 'success')
        else:
            flash("Kategori silinemedi veya bulunamadı.", 'danger')
    except ValueError as e:
        flash(f"Kategori silinemedi: {str(e)}", 'danger')
    except Exception as e:
        flash(f"Kategori silinirken hata oluştu: {str(e)}", 'danger')

    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/forgive_fines/<int:user_id>', methods=['POST'])
@admin_required
def forgive_fines(user_id):
    # Kullanıcıyı bul (Repository pattern kullanarak)
    user_repo = UserRepository()
    user = user_repo.get_by_id(user_id)

    if not user:
        flash(f"Kullanıcı (ID: {user_id}) bulunamadı.", 'danger')
        return redirect(url_for('admin_bp.admin_page'))

    # LoanService ile ceza affını gerçekleştir
    success = LoanService.forgive_fines(user_id)

    if success:
        flash(f"'{user.username}' adlı kullanıcının tüm cezaları başarıyla affedildi (Sıfırlandı).", 'success')
    else:
        # Hata genellikle veritabanı prosedüründe (sp_ForgiveFines) bir sorun olduğunda oluşur.
        flash(f"Cezalar affedilemedi. Veritabanı prosedürü hatası olabilir.", 'danger')

    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/update_book/<int:book_id>', methods=['POST'])
@admin_required
def update_book(book_id):
    """Kitap güncelleme route'u"""
    try:
        book = BookService.get_book_by_id(book_id)
        if not book:
            flash(f"Kitap (ID: {book_id}) bulunamadı.", 'danger')
            return redirect(url_for('admin_bp.admin_page'))

        # Form verilerini al
        update_data = {
            'name': request.form.get('name'),
            'author': request.form.get('author'),
            'category': request.form.get('category'),
            'barcode': request.form.get('barcode'),
            'description': request.form.get('description')
        }

        # Resim güncelleme kontrolü
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                image_file_name = FileService.save_picture(image_file)
                update_data['image_file'] = image_file_name

        # Kitabı güncelle
        updated_book = BookService.update_book(book_id, update_data)
        
        if updated_book:
            flash(f"'{updated_book.name}' başarıyla güncellendi.", 'success')
        else:
            flash("Kitap güncellenemedi.", 'danger')

    except Exception as e:
        flash(f"Kitap güncellenirken hata oluştu: {str(e)}", 'danger')

    return redirect(url_for('admin_bp.admin_page'))


@admin_bp.route('/admin/delete_book/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    """Kitap silme route'u"""
    try:
        book = BookService.get_book_by_id(book_id)
        if not book:
            flash(f"Kitap (ID: {book_id}) bulunamadı.", 'danger')
            return redirect(url_for('admin_bp.admin_page'))

        # Aktif ödünç kontrolü
        active_borrows = LoanService.borrow_repo.get_all_active()
        book_has_active_borrows = any(b.book_id == book_id for b in active_borrows)
        
        if book_has_active_borrows:
            flash(f"'{book.name}' kitabı şu anda ödünç alınmış durumda. Önce iade edilmesi gerekir.", 'danger')
            return redirect(url_for('admin_bp.admin_page'))

        # Kitabı sil
        success = BookService.delete_book(book_id)
        
        if success:
            flash(f"'{book.name}' başarıyla silindi.", 'success')
        else:
            flash("Kitap silinemedi.", 'danger')

    except Exception as e:
        flash(f"Kitap silinirken hata oluştu: {str(e)}", 'danger')

    return redirect(url_for('admin_bp.admin_page'))