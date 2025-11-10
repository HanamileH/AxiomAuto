from flask import Flask, render_template, redirect
import database

app = Flask(__name__)

# Главная страница (каталог)
@app.route('/')
def main():
   all_models = database.get_catalog()
   
   return render_template('catalog.html', models=all_models)


# Страница описания автомобиля
@app.route('/car/<model_id>')
def car(model_id):
   model = database.get_model_data(model_id)
   
   if model:
      return render_template('car.html', model=model)
   else:
      return render_template('404.html'), 404


# Страница менеджера
@app.route('/staff/<entity_name>')
def staff(entity_name):
   entities = database.ENTITIES_TYPES
   current_entity = None
   
   for entity in entities:
      if entity["tab_name"] == entity_name:
         current_entity = entity
         break
   
   if current_entity:
      return render_template("staff.html", entities=entities, current_entity=current_entity)
   else:
      return render_template('404.html'), 404


# Информация о компании
@app.route('/about')
def about():
   return render_template('about.html')


# Страница регистрации пользователя
@app.route('/register')
def register():
   return render_template('register.html')


# Страница авторизации пользователя
@app.route('/login')
def login():
   return render_template('login.html')


# Стрница профиля пользователя
@app.route('/profile')
def profile():
   return render_template('profile.html')


# Страница ошибки 404
@app.errorhandler(404)
def page_not_found(e):
   return render_template('404.html'), 404


# Запускаем приложение
if __name__ == '__main__':
   database.init_db()
   app.run(debug=True)