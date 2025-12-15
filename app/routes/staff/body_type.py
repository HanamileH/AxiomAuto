from flask import Blueprint, request, jsonify
from app.db.body_type import Body_type
from app.db.user import manager_required

bp = Blueprint('staff/body_type', __name__)

# GET-запрос
@bp.route('/api/body_types', methods=['GET'])
#@manager_required
def get_brands():
    """Получить все кузовы"""
    try:
        brands, error = Body_type.get_all()
        
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
@bp.route('/api/body_types', methods=['POST'])
#@manager_required
def create_brand():
    """Создать новый тип кузова"""
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
        
        id, error = Body_type.create(name)
        
        if error:
            return jsonify({
                'success': False, 
                'error': error
            }), 400
        
        return jsonify({
            'success': True, 
            'id': id, 
            'message': 'Тип успешно создан'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


# PUT-запрос
@bp.route('/api/body_types/<int:brand_id>', methods=['PUT'])
#@manager_required
def update_brand(brand_id):
   """Обновить тип кузова"""
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
      
      success, error = Body_type.update(brand_id, name)
      
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
@bp.route('/api/body_types/<int:brand_id>', methods=['DELETE'])
#@manager_required
def delete_brand(brand_id):
    """Удалить тип кузова"""
    try:
        success, error = Body_type.delete(brand_id)
        
        if error:
            return jsonify({
                'success': False, 
                'error': error
            }), 400
        
        return jsonify({
            'success': True, 
            'message': 'Тип успешно удален'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500