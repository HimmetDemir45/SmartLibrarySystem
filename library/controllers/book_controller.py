from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from library.forms import BorrowBookForm, ReturnBookForm, EditBookForm
from library.services.book_service import BookService
from library.services.loan_service import LoanService

book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/library', methods=['GET', 'POST'])
@login_required
def library_page():
    borrow_form = BorrowBookForm()
    return_form = ReturnBookForm()

    if request.method == "POST":
        # --- 1. ÖDÜNÇ ALMA İŞLEMİ ---
        borrowed_book_id = request.form.get('borrowed_book_id')
        if borrowed_book_id:
            result = LoanService.borrow_book(current_user.id, borrowed_book_id)
            if result['success']:
                flash(result['message'], category='success')
            else:
                flash(result['message'], category='danger')

        # --- 2. İADE ETME İŞLEMİ ---
        returned_book_id = request.form.get('returned_book_id')
        if returned_book_id:
            result = LoanService.return_book(current_user.id, returned_book_id)
            if result['success']:
                flash(result['message'], category='success')
            else:
                flash(result['message'], category='danger')

        # İşlem bitince sayfayı yenile
        return redirect(url_for('book_bp.library_page'))

    # --- GET İSTEĞİ (SAYFA GÖRÜNTÜLEME) ---
    # Eksik olan kısım burasıydı:
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q')

    # Kitapları ve kullanıcının üzerindekileri çekiyoruz
    books_pagination = BookService.search_books(search_query, page=page)
    owned_books = LoanService.get_user_active_loans(current_user.id)

    return render_template('library.html',
                           items=books_pagination,
                           purchase_form=borrow_form,
                           owned_items=owned_books,
                           selling_form=return_form)


# --- KİTAP SİLME (Admin Yetkisiyle) ---
@book_bp.route('/delete_book_web/<int:id>')
@login_required
def delete_book_web(id):
    if not current_user.is_admin:
        flash("Yetkiniz yok!", category='danger')
        return redirect(url_for('book_bp.library_page'))

    success = BookService.delete_book(id)
    if success:
        flash("Kitap silindi.", 'success')
    else:
        flash("Kitap silinemedi.", 'danger')

    return redirect(url_for('book_bp.library_page'))


# --- KİTAP DÜZENLEME (Admin Yetkisiyle) ---
@book_bp.route('/edit_book_web/<int:id>', methods=['POST'])
@login_required
def edit_book_web(id):
    if not current_user.is_admin:
        flash("Bu işlem için yetkiniz yok!", category='danger')
        return redirect(url_for('book_bp.library_page'))

    # Formu request verisiyle doldur
    form = EditBookForm(request.form)

    # Validasyon kontrolü
    if form.validate():
        data = {
            'name': form.name.data,
            'author': form.author.data,
            'category': form.category.data,
            'barcode': form.barcode.data,
            'description': form.description.data
        }

        # Resim güncelleme kontrolü
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                from library.services.file_service import FileService
                image_file_name = FileService.save_picture(image_file)
                data['image_file'] = image_file_name

        updated_book = BookService.update_book(id, data)

        if updated_book:
            flash(f"{updated_book.name} bilgileri güncellendi.", category='success')
        else:
            flash("Kitap bulunamadı veya güncelleme başarısız.", category='danger')
    else:
        # Form validasyon hatalarını göster
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Hata ({field}): {error}", category='danger')

    return redirect(url_for('book_bp.library_page'))

@book_bp.route('/pay_fines', methods=['POST'])
@login_required
def pay_fines():
    # Tüm işlemi servise devrettik
    result = LoanService.pay_fines_via_budget(current_user.id)

    if result['success']:
        flash(result['message'], "success")
    else:
        # Hata mesajı servisten ne gelirse onu gösteriyoruz (Yetersiz bakiye vb.)
        flash(result['message'], "danger")

    return redirect(url_for('main_bp.profile_page'))