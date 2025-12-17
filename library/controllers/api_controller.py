from flask_login import current_user
from library.services.loan_service import LoanService
from flask import Blueprint, request, render_template, jsonify
from library.services.book_service import BookService

api_bp = Blueprint('api_bp', __name__)

# --- GET İŞLEMLERİ (SAYFALAMA EKLENDİ) ---

@api_bp.route('/api/books', methods=['GET'])
def get_all_books():
    # URL'den sayfa numarasını al (örn: /api/books?page=2), yoksa 1. sayfa
    page = request.args.get('page', 1, type=int)

    # Servisten Pagination objesi döner
    pagination = BookService.get_all_books(page=page)

    output = []
    for book in pagination.items:  # .items diyerek o sayfadaki kitapları alıyoruz
        book_data = {
            'id': book.id,
            'name': book.name,
            'barcode': book.barcode,
            'description': book.description,
            'author': book.author.name if book.author else "Bilinmiyor",
            'category': book.category.name if book.category else "Genel",
            'is_available': book.is_available,
            'image_file': book.image_file
        }
        output.append(book_data)

    return jsonify({
        'success': True,
        'data': output,
        'meta': {
            'page': pagination.page,
            'pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200

@api_bp.route('/api/book/<int:id>', methods=['GET'])
def get_book(id):
    book = BookService.get_book_by_id(id)
    if book:
        return jsonify({
            'success': True,
            'data': {
                'id': book.id,
                'name': book.name,
                'barcode': book.barcode,
                'author': book.author.name,
                'is_available': book.is_available
            }
        }), 200
    return jsonify({'success': False, 'message': 'Kitap bulunamadı'}), 404

# --- POST (ÖDÜNÇ/İADE) İŞLEMLERİ (BARKOD SİSTEMİNE GEÇİLDİ) ---

@api_bp.route('/api/borrow', methods=['POST'])
def borrow_book_api():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Giriş yapmalısınız.'}), 401

    # Artık isim yerine BARKOD bekliyoruz
    barcode = request.form.get('barcode')

    if not barcode:
        return jsonify({'success': False, 'message': 'Barkod parametresi zorunludur.'}), 400

    book = BookService.get_book_by_barcode(barcode)

    if not book:
        return jsonify({'success': False, 'message': 'Bu barkoda sahip kitap bulunamadı.'}), 404

    # Ödünç alma servisini çağır
    result = LoanService.borrow_book(current_user.id, book.id)

    status = 200 if result['success'] else 400
    return jsonify(result), status

@api_bp.route('/api/return', methods=['POST'])
def return_book_api():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Giriş yapmalısınız.'}), 401

    barcode = request.form.get('barcode')

    if not barcode:
        return jsonify({'success': False, 'message': 'Barkod parametresi zorunludur.'}), 400

    book = BookService.get_book_by_barcode(barcode)

    if not book:
        return jsonify({'success': False, 'message': 'Bu barkoda sahip kitap bulunamadı.'}), 404

    result = LoanService.return_book(current_user.id, book.id)

    status = 200 if result['success'] else 400
    return jsonify(result), status

@api_bp.route('/api/search_books', methods=['GET'])
def search_books_live():
    """Canlı arama (HTML partial döndürür)"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    books_pagination = BookService.search_books(query, page=page)

    return render_template('includes/book_list.html', items=books_pagination)