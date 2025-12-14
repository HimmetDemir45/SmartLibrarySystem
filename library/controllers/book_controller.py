from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from library.forms import AddBookForm, BorrowBookForm, ReturnBookForm
from library.services.book_service import BookService
from library.services.loan_service import LoanService

book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/library', methods=['GET', 'POST'])
@login_required
def library_page():
    borrow_form = BorrowBookForm()
    return_form = ReturnBookForm()
    add_book_form = AddBookForm()

    if request.method == "POST":
        # --- 1. KİTAP EKLEME (Sadece Admin) ---
        if add_book_form.validate_on_submit():
            BookService.add_book(
                name=add_book_form.name.data,
                author_name=add_book_form.author.data,
                category_name=add_book_form.category.data,
                barcode=add_book_form.barcode.data,
                description=add_book_form.description.data
            )
            flash(f"{add_book_form.name.data} başarıyla eklendi!", category='success')
            return redirect(url_for('book_bp.library_page'))

        # --- 2. ÖDÜNÇ ALMA İŞLEMİ (EKLENEN KISIM) ---
        borrowed_book_name = request.form.get('borrowed_book_name')
        if borrowed_book_name:
            # İsme göre kitabı bul
            book = BookService.get_book_by_name(borrowed_book_name)
            if book:
                # Servis ile ödünç al
                result = LoanService.borrow_book(current_user.id, book.id)

                if result['success']:
                    flash(result['message'], category='success')
                else:
                    flash(result['message'], category='danger')
            else:
                flash("Kitap bulunamadı.", category='danger')

        # --- 3. İADE ETME İŞLEMİ (EKLENEN KISIM) ---
        returned_book_name = request.form.get('returned_book_name')
        if returned_book_name:
            book = BookService.get_book_by_name(returned_book_name)
            if book:
                result = LoanService.return_book(current_user.id, book.id)

                if result['success']:
                    flash(result['message'], category='success')
                else:
                    flash(result['message'], category='danger')
            else:
                flash("İade edilecek kitap bulunamadı.", category='danger')

        # İşlem bitince sayfayı yenile (GET isteği yap)
        return redirect(url_for('book_bp.library_page'))

    # --- GET İSTEĞİ (SAYFA GÖRÜNTÜLEME) ---
    search_query = request.args.get('q')
    books = BookService.search_books(search_query)

    # Kullanıcının elindeki kitapları bul (Modal için gerekli)
    owned_books = LoanService.get_user_active_loans(current_user.id)

    return render_template('library.html', items=books, purchase_form=borrow_form,
                           owned_items=owned_books, selling_form=return_form,
                           add_book_form=add_book_form)

# --- Diğer Rotalar (Silme, Düzenleme) ---
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

@book_bp.route('/edit_book_web/<int:id>', methods=['POST'])
@login_required
def edit_book_web(id):
    if not current_user.is_admin:
        flash("Bu işlem için yetkiniz yok!", category='danger')
        return redirect(url_for('book_bp.library_page'))

    data = {
        'name': request.form.get('name'),
        'author': request.form.get('author'),
        'category': request.form.get('category'),
        'barcode': request.form.get('barcode'),
        'description': request.form.get('description')
    }

    updated_book = BookService.update_book(id, data)

    if updated_book:
        flash(f"{updated_book.name} bilgileri güncellendi.", category='success')
    else:
        flash("Kitap bulunamadı veya güncelleme başarısız.", category='danger')

    return redirect(url_for('book_bp.library_page'))