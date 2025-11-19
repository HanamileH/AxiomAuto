from flask import Blueprint, render_template

bp = Blueprint('auth', __name__)

# Страница регистрации пользователя
@bp.route('/register')
def register():
   return render_template('register.html')


# Страница авторизации пользователя
@bp.route('/login')
def login():
   return render_template('login.html')


# Стрница профиля пользователя
@bp.route('/profile')
def profile():
   return render_template('profile.html')