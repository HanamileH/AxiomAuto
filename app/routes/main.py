import string
import random

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app import db

bp = Blueprint('main', __name__)

# Главная страница (каталог)
@bp.route('/')
def main():
   all_models = db.get_catalog()

   return render_template('catalog.html', models=all_models)


# Страница описания автомобиля
@bp.route('/car/<model_id>')
def car(model_id):
   model = db.get_model_data(model_id)
   
   if model:
      return render_template('car.html', model=model)
   else:
      return abort(404)


# Страница менеджера
@bp.route('/staff/<entity_name>')
@login_required
def staff(entity_name):
   if not current_user.role in ['admin', 'manager']:
      return abort(403)

   entities = db.ENTITIES_TYPES
   current_entity = None
   
   for entity in entities:
      if entity["tab_name"] == entity_name:
         current_entity = entity
         break
   
   if current_entity:
      # Генерируем случайные строки для отображения во время загрузки
      template_rows = []

      for i in range(10):
         template_rows.append(''.join([random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 10))]))

      return render_template(f"staff/{entity['tab_name']}.html", entities=entities, current_entity=current_entity, template_rows=template_rows)
   else:
      return abort(404)


# Информация о компании
@bp.route('/about')
def about():
   return render_template('about.html')


# Страница ошибка 401
@bp.errorhandler(401)
def unauthorized(e):
   return render_template(
      'error.html',
      error_title='Ошибка 401 - Неавторизованный доступ',
      error_code='401',
      error_message='Неавторизованный доступ.',
      error_description='Вы не авторизованы. Пожалуйста, авторизуйтесь для доступа к этой странице.'
   ), 401


# Страница ошибки 403
@bp.errorhandler(403)
def forbidden(e):
   return render_template(
      'error.html',
      error_title='Ошибка 403 - Доступ запрещен',
      error_code='403',
      error_message='Доступ к странице запрещен.',
      error_description='У вас недостаточно прав для просмотра этой страницы.'
   ), 403


# Страница ошибки 404
@bp.errorhandler(404)
def page_not_found(e):
   return render_template(
      'error.html',
      error_title='Ошибка 404 - Страница не найдена',
      error_code='404',
      error_message='Страница не найдена.',
      error_description='Запрашиваемая страница не существует или была удалена.'
   ), 404

# Страница ошибки 500
@bp.errorhandler(500)
def internal_server_error(e):
   return render_template(
      'error.html',
      error_title='Ошибка 500 - Внутренняя ошибка сервера',
      error_code='500',
      error_message='Внутренняя ошибка сервера.',
      error_description='Произошла ошибка на сервере. Попробуйте повторить запрос позже или обратитесь к системному администратору.'
   ), 500