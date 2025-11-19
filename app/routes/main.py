from flask import Blueprint, render_template
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
      return render_template('404.html'), 404


# Страница менеджера
@bp.route('/staff/<entity_name>')
@login_required
def staff(entity_name):
   if not current_user.role in ['admin', 'manager']:
      return render_template('403.html'), 403

   entities = db.ENTITIES_TYPES
   current_entity = None
   
   for entity in entities:
      if entity["tab_name"] == entity_name:
         current_entity = entity
         break
   
   if current_entity:
      return render_template(f"staff/{entity['tab_name']}.html", entities=entities, current_entity=current_entity)
   else:
      return render_template('404.html'), 404


# Информация о компании
@bp.route('/about')
def about():
   return render_template('about.html')


# Страница ошибки 404
@bp.errorhandler(404)
def page_not_found(e):
   return render_template('404.html'), 404