from flask import Blueprint, jsonify, request
from flask_login import current_user
from library.services.book_service import BookService
from library.services.loan_service import LoanService

api_bp = Blueprint('api_bp', __name__)

# --- GET İŞLEMLERİ ---

@api_bp.route('/api/books', methods=['GET'])
def get_all_books():
    books = BookService.get_all_books()
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

    return jsonify({'success': True, 'data': output}), 200

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

# --- POST (ÖDÜNÇ/İADE) İŞLEMLERİ ---

@api_bp.route('/api/borrow', methods=['POST'])
def borrow_book_api():
    # API Testleri için login kontrolünü kapatabilir veya token bazlı yapabilirsin.
    # Şimdilik basit tutuyoruz:
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Giriş yapmalısınız.'}), 401

    book_name = request.form.get('book_name')
    # İsimden ID bulmak için basit bir mantık veya direkt ID alabiliriz.
    # Mevcut yapına sadık kalarak isimden kitap bulalım:
    books = BookService.search_books(book_name)
    if not books:
        return jsonify({'success': False, 'message': 'Kitap bulunamadı'}), 404

    book = books[0] # İlk eşleşen
    result = LoanService.borrow_book(current_user.id, book.id)

    status = 200 if result['success'] else 400
    return jsonify(result), status

@api_bp.route('/api/return', methods=['POST'])
def return_book_api():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Giriş yapmalısınız.'}), 401

    book_name = request.form.get('book_name')
    books = BookService.search_books(book_name)
    if not books:
        return jsonify({'success': False, 'message': 'Kitap bulunamadı'}), 404

    book = books[0]
    result = LoanService.return_book(current_user.id, book.id)

    status = 200 if result['success'] else 400
    return jsonify(result), status