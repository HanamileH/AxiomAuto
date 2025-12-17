from flask import Blueprint, request, jsonify
from app.db import Brand, manager_required

bp = Blueprint('staff/brand', __name__)

# GET-запрос
@bp.route('/api/brands', methods=['GET'])
@manager_required
def get_brands():
    """Получить все бренды"""
    try:
        brands, error = Brand.get_all()
        
        if error:
            return jsonify({
                'success': False, 
                'error': error
            }), 500
        
        return jsonify({
            'success': True, 
            'data': brands if brands else []
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


# POST-запрос
@bp.route('/api/brands', methods=['POST'])
@manager_required
def create_brand():
    """Создать новый бренд"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False, 
                'error': 'Неверный формат данных. Ожидается JSON'
            }), 400
            
        name = data.get('name')
        
        if not name:
            return jsonify({
                'success': False, 
                'error': 'Название обязательно'
            }), 400
        
        id, error = Brand.create(name)
        
        if error:
            return jsonify({
                'success': False, 
                'error': error
            }), 400
        
        return jsonify({
            'success': True, 
            'id': id, 
            'message': 'Бренд успешно создан'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


# PUT-запрос
@bp.route('/api/brands/<int:brand_id>', methods=['PUT'])
@manager_required
def update_brand(brand_id):
    """Обновить бренд"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False, 
                'error': 'Неверный формат данных. Ожидается JSON'
            }), 400
            
        name = data.get('name')
        
        if not name:
            return jsonify({
                'success': False, 
                'error': 'Название обязательно'
            }), 400
        
        success, error = Brand.update(brand_id, name)
        
        if error:
            return jsonify({
                'success': False, 
                'error': error
            }), 400
        
        return jsonify({
            'success': True, 
            'message': 'Бренд успешно обновлен'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


# DELETE-запрос
@bp.route('/api/brands/<int:brand_id>', methods=['DELETE'])
@manager_required
def delete_brand(brand_id):
    """Удалить бренд"""
    try:
        success, error = Brand.delete(brand_id)
        
        if error:
            return jsonify({
                'success': False, 
                'error': error
            }), 400
        
        return jsonify({
            'success': True, 
            'message': 'Бренд успешно удален'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500