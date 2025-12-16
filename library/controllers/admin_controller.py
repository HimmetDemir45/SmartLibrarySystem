from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from library.forms import AddAuthorForm, AddCategoryForm
from library.services.author_service import AuthorService
from library.services.category_service import CategoryService
from library import db
from library.models import User
from library.services.loan_service import LoanService

admin_bp = Blueprint('admin_bp', __name__)


def admin_required(f):
    """Admin yetkisi gerektiren custom decorator."""
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Bu sayfaya erişim yetkiniz yok.", category='danger')
            return redirect(url_for('main_bp.home_page'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_required # Admin yetkisi kontrolü
def admin_page():
    # Formları oluştur
    author_form = AddAuthorForm()
    category_form = AddCategoryForm()

    # Yazar ve Kategori listelerini çek
    authors = AuthorService.get_all_authors()
    categories = CategoryService.get_all_categories()

    # Tüm kullanıcıları çek
    all_users = User.query.all()

    if request.method == 'POST':
        # Yazar Ekleme İşlemi
        if author_form.validate_on_submit() and 'author_submit' in request.form:
            AuthorService.add_author(author_form.name.data)
            flash(f"Yazar '{author_form.name.data}' başarıyla eklendi.", 'success')
            return redirect(url_for('admin_bp.admin_page'))

        # Kategori Ekleme İşlemi
        elif category_form.validate_on_submit() and 'category_submit' in request.form:
            CategoryService.add_category(category_form.name.data)
            flash(f"Kategori '{category_form.name.data}' başarıyla eklendi.", 'success')
            return redirect(url_for('admin_bp.admin_page'))

    return render_template('admin_dashboard.html',
                           author_form=author_form,
                           category_form=category_form,
                           authors=authors,
                           categories=categories,
                            all_users=all_users)


# --- DÜZENLEME ROTASI (Popup Modal ile yapılacak varsayılır) ---
@admin_bp.route('/admin/update_author/<int:author_id>', methods=['POST'])
@admin_required
def update_author(author_id):
    new_name = request.form.get('name')
    if not new_name:
        flash("İsim boş bırakılamaz.", 'danger')
        return redirect(url_for('admin_bp.admin_page'))

    success = AuthorService.update_author(author_id, new_name)
    if success:
        flash(f"Yazar (ID: {author_id}) başarıyla güncellendi.", 'success')
    else:
        flash("Yazar güncellenemedi veya bulunamadı.", 'danger')

    return redirect(url_for('admin_bp.admin_page'))


# --- SİLME ROTASI ---
@admin_bp.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    # Gerçek uygulamada önce bağlı kitap kontrolü yapılmalıdır.
    success = CategoryService.delete_category(category_id)
    if success:
        flash("Kategori başarıyla silindi.", 'success')
    else:
        flash("Kategori silinemedi (Belki bağlı kitaplar var?).", 'danger')

    return redirect(url_for('admin_bp.admin_page'))

@admin_bp.route('/admin/forgive_fines/<int:user_id>', methods=['POST'])
@admin_required
def forgive_fines(user_id):
    # Kullanıcıyı bul
    user = User.query.get(user_id)

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