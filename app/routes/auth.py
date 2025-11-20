from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required
from app.db.user import register_user as db_register_user
from app.db.user import login_user as db_login_user

bp = Blueprint('auth', __name__)

# Регистрация пользователя
@bp.route('/register', methods=['GET', 'POST'])
def register():
   # POST-запрос на регистрацию
   if request.method == 'POST':
      # Парсим данные
      try:
         data = request.get_json()
         name = data['name']
         surname = data['surname']
         patronymic = data['patronymic']
         phone = data['phone']
         email = data['email']
         password = data['password']
      except:
         data = {'status': 'error', 'error_text': 'incorrect request'}
         return jsonify(data), 400

      # Регистрируем пользователя
      user_id, error_text = db_register_user(name, surname, patronymic, phone, email, password, 'user')

      # Если регистрация успешна, возвращаем код 200
      if user_id:
         # Сохраняем пользователя в сессию
         user, error_text = db_login_user(email, password)
         
         if user:
            login_user(user, remember=True)
            session.permanent = True
         
         data = {'status': 'success'}
         return jsonify(data), 200
      # Иначе возвращаем код 400 с текстом ошибки
      else:
         data = {'status': 'error', 'error_text': error_text}
         return jsonify(data), 400

   # Страница регистрации
   return render_template('register.html')


# Авторизация пользователя
@bp.route('/login', methods=['GET', 'POST'])
def login():
   # POST-запрос на вход в аккаунт
   if request.method == 'POST':
      # Парсим данные
      try:
         data = request.get_json()
         email = data['email']
         password = data['password']
      except:
         data = {'status': 'error', 'error_text': 'incorrect request'}
         return jsonify(data), 400

      # Авторизуем пользователя
      user, error_text = db_login_user(email, password)

      # Если авторизация успешна, возвращаем код 200
      if user:
         # Сохраняем пользователя в сессию
         login_user(user, remember=True)
         session.permanent = True
         
         data = {'status': 'success'}
         return jsonify(data), 200
      # Иначе возвращаем код 400 с текстом ошибки
      else:
         data = {'status': 'error', 'error_text': error_text}
         return jsonify(data), 400

   return render_template('login.html')


# Стрница профиля пользователя
@bp.route('/profile')
@login_required
def profile():
   return render_template('profile.html')


# Выход из системы
@bp.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('auth.login'))