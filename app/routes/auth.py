from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.db.user import User, register_user as db_register_user, login_user as db_login_user

bp = Blueprint('auth', __name__)

# Страница регистрации пользователя
@bp.route('/register', methods=['GET', 'POST'])
def register():
   if request.method == 'POST':
      name = request.form['name']
      surname = request.form['surname']
      patronymic = request.form['patronymic']
      phone = request.form['phone']
      email = request.form['email']
      password = request.form['password']

      user_id = db_register_user(name, surname, patronymic, phone, email, password)

      if user_id:
         return redirect(url_for('auth.login'))
      else:
         return render_template('register.html', error='Проверьте корректность всех полей!')

   return render_template('register.html')


# Страница авторизации пользователя
@bp.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']

      user = db_login_user(email, password)

      if user:
         login_user(user)
         return redirect(url_for('auth.profile'))
      else:
         return render_template('login.html', error='Неверный логин или пароль!')

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