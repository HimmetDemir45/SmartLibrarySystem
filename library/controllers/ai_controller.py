from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from library.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI sohbet endpoint'i"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Mesaj boş olamaz.'
            }), 400
        
        response = AIService.chat(current_user.id, message)
        
        return jsonify({
            'success': True,
            'response': response
        }), 200
        
    except Exception as e:
        logger.error(f"AI chat hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {str(e)}'
        }), 500

@ai_bp.route('/ai/recommendations', methods=['GET'])
@login_required
def ai_recommendations():
    """Kitap önerileri endpoint'i"""
    try:
        response = AIService.get_book_recommendations(current_user.id)
        
        return jsonify({
            'success': True,
            'recommendations': response
        }), 200
        
    except Exception as e:
        logger.error(f"AI öneriler hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {str(e)}'
        }), 500

@ai_bp.route('/ai/book-info', methods=['POST'])
@login_required
def ai_book_info():
    """Kitap bilgisi endpoint'i"""
    try:
        data = request.get_json()
        book_name = data.get('book_name', '').strip()
        
        if not book_name:
            return jsonify({
                'success': False,
                'message': 'Kitap adı boş olamaz.'
            }), 400
        
        response = AIService.get_book_info(book_name)
        
        return jsonify({
            'success': True,
            'info': response
        }), 200
        
    except Exception as e:
        logger.error(f"AI kitap bilgisi hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {str(e)}'
        }), 500

@ai_bp.route('/ai/author-info', methods=['POST'])
@login_required
def ai_author_info():
    """Yazar bilgisi endpoint'i"""
    try:
        data = request.get_json()
        author_name = data.get('author_name', '').strip()
        
        if not author_name:
            return jsonify({
                'success': False,
                'message': 'Yazar adı boş olamaz.'
            }), 400
        
        response = AIService.get_author_info(author_name)
        
        return jsonify({
            'success': True,
            'info': response
        }), 200
        
    except Exception as e:
        logger.error(f"AI yazar bilgisi hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {str(e)}'
        }), 500

@ai_bp.route('/ai/assistant')
@login_required
def ai_assistant_page():
    """AI asistan sayfası"""
    return render_template('ai_assistant.html')

@ai_bp.route('/ai/check', methods=['GET'])
def ai_check():
    """Ollama bağlantı kontrolü"""
    is_connected = AIService.check_ollama_connection()
    return jsonify({
        'success': is_connected,
        'message': 'Ollama servisi çalışıyor' if is_connected else 'Ollama servisine bağlanılamadı'
    }), 200 if is_connected else 503

