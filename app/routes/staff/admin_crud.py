from flask import Blueprint, request, jsonify
from app.db import Brand, Body_type, Color, manager_required

OBJECTS_MATCH = {
   'brands': Brand,
   'body_types': Body_type,
   'colors': Color
}


bp = Blueprint('staff/admin_crud', __name__)

# GET-запрос на получение всех записей объекта
@bp.route('/api/crud/<object_name>', methods=['GET'])
@manager_required
def get_all(object_name):
   try:
      object_name = object_name.strip().lower()

      # Получаем класс нужного объекта
      object_class = OBJECTS_MATCH.get(object_name)

      if object_class is None:
         return jsonify({
            'success': False,
            'error': f'Object {object_name} not found'
         }), 404
      
      # Получаем все объекты класса
      rows, error = object_class.get_all()

      if error:
         return jsonify({
            'success': False,
            'error': error
         }), 500
      
      # Возвращаем объекты
      return jsonify({
         'success': True,
         'data': rows
      })
   
   except Exception as e:
      return jsonify({
         'success': False,
         'error': str(e)
      }), 500


# POST-запрос на создание нового объекта
@bp.route('/api/crud/<object_name>', methods=['POST'])
@manager_required
def create(object_name):
   try:
      object_name = object_name.strip().lower()

      # Получаем класс нужного объекта
      object_class = OBJECTS_MATCH.get(object_name)

      if object_class is None:
         return jsonify({
            'success': False,
            'error': f'Object {object_name} not found'
         }), 404
      
      # Получаем данные из запроса
      data = request.get_json()

      # ----- Добавляем запись -----
      # Производители
      if object_name == 'brands':
         name = data.get('name')

         if not name:
            return jsonify({
               'success': False,
               'error': 'Name is required'
            }), 400
         
         id, error = Brand.create(name=name)

      # Типы кузовов
      elif object_name == 'body_types':
         name = data.get('name')

         if not name:
            return jsonify({
               'success': False,
               'error': 'Name is required'
            }), 400

         id, error = Body_type.create(name=name)

      # Цвета
      elif object_name == 'colors':
         name = data.get('name')
         hex_code = data.get('hex_code')

         if not name:
            return jsonify({
               'success': False,
               'error': 'Name is required'
            }), 400

         if not hex_code:
            return jsonify({
               'success': False,
               'error': 'Hex code is required'
            }), 400
         
         id, error = Color.create(name=name, hex_code=hex_code)
      
      # Неизвестный объект
      else:
         return jsonify({
            'success': False,
            'error': f'Object {object_name} not found'
         }), 404
      # -----------------------------
      
      # Обработка ошибок
      if error:
         return jsonify({
            'success': False,
            'error': error
         }), 500

      # Возвращаем результат
      return jsonify({
         'success': True,
         'id': id
      }), 200
   
   except Exception as e:
      return jsonify({
         'success': False,
         'error': str(e)
      }), 500
      
   
# PUT-запрос на изменение объекта
@bp.route('/api/crud/<object_name>/<int:id>', methods=['PUT'])
@manager_required
def update(object_name, id):
   try:
      object_name = object_name.strip().lower()

      # Получаем класс нужного объекта
      object_class = OBJECTS_MATCH.get(object_name)

      if object_class is None:
         return jsonify({
            'success': False,
            'error': f'Object {object_name} not found'
         }), 404

      # Получаем данные из запроса
      data = request.get_json()

      # ----- Обновляем запись -----
      # Производители
      if object_name == 'brands':
         name = data.get('name')

         if not name:
            return jsonify({
               'success': False,
               'error': 'Name is required'
            }), 400

         _, error = Brand.update(id=id, name=name)

      # Типы кузовов
      elif object_name == 'body_types':
         name = data.get('name')

         if not name:
            return jsonify({
               'success': False,
               'error': 'Name is required'
            }), 400

         _, error = Body_type.update(id=id, name=name)

      # Цвета
      elif object_name == 'colors':
         name = data.get('name')
         hex_code = data.get('hex_code')

         if not name or not hex_code:
            return jsonify({
               'success': False,
               'error': 'Name or hex code are required'
            }), 400
         
         _, error = Color.update(id=id, name=name, hex_code=hex_code)

      # Неизвестный объект
      else:
         return jsonify({
            'success': False,
            'error': f'Object {object_name} not found'
         }), 404
      # -----------------------------
      
      # Обработка ошибок
      if error:
         return jsonify({
            'success': False,
            'error': error
         }), 500
      
      # Возвращаем результат
      return jsonify({
         'success': True
      })
   
   except Exception as e:
      return jsonify({
         'success': False,
         'error': str(e)
      }), 500
   

# DELETE-запрос на удаление объекта
@bp.route('/api/crud/<object_name>/<int:id>', methods=['DELETE'])
@manager_required
def delete(object_name, id):
   try:
      object_name = object_name.strip().lower()

      # Получаем класс нужного объекта
      object_class = OBJECTS_MATCH.get(object_name)

      if object_class is None:
         return jsonify({
            'success': False,
            'error': f'Object {object_name} not found'
         }), 404

      # Удаляем запись
      success, error = object_class.delete(id=id)

      # Обработка ошибок
      if error:
         return jsonify({
            'success': False,
            'error': error
         }), 500

      # Возвращаем результат
      return jsonify({
         'success': True
      }), 200
   
   except Exception as e:
      return jsonify({
         'success': False,
         'error': str(e)
      }), 500