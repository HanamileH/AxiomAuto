import re
from functools import wraps
from flask import abort
from flask_login import UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .connection import db


class User(UserMixin):
   def __init__(self, id, name, surname, patronymic, email, password_hash, role='user'):
      self.id = id
      self.name = name
      self.surname = surname
      self.patronymic = patronymic
      self.email = email
      self.password_hash = password_hash
      self.role = role


   @staticmethod
   def get_by_id(user_id):
      with db.get_cursor() as cursor:
         cursor.execute("""
         SELECT
            c.id AS id,
            c.name AS name,
            c.surname AS surname,
            c.patronymic AS patronymic,
            u.email AS email,
            u.password_hash AS password_hash,
            u.role AS role
         FROM users u
         JOIN client c
         ON u.id = c.id
         WHERE u.id = %s            
         """, (user_id, ))

         row = cursor.fetchone()

         if row:
            return User(*row)
         return None


def admin_required(f):
   """Декоратор для проверки прав доступа.
   Доступно только для пользователей с ролью 'admin'
   """
   @wraps(f)
   def decorated_function(*args, **kwargs):
      if not current_user.is_authenticated or current_user.role != 'admin':
         return abort(403)
      return f(*args, **kwargs)
   return decorated_function


def manager_required(f):
   """Декоратор для проверки прав доступа.
   Доступно только для пользователей с ролью 'manager' или 'admin'
   """
   @wraps(f)
   def decorated_function(*args, **kwargs):
      if not current_user.is_authenticated or current_user.role not in ['manager', 'admin']:
         return abort(403)
      return f(*args, **kwargs)
   return decorated_function


def register_user(name, surname, patronymic, email, password, role='user'):
   """Регистрация нового пользователя.

   Args:
      name (str): Имя.
      surname (str): Фамилия.
      patronymic (str): Отчество.
      email (str): Email.
      password (str): Пароль.
      role (str): Роль пользователя (По умолчанию 'user').

   Returns:
      Int: ID пользователя (или False, если добавление не удалось)
      String: Текст ошибки (если добавление не удалось)
   
   """
   
   # Регулярные выражения для валидации
   full_name_pattern = r'^[a-zA-Zа-яёА-ЯЁ\s]+$' # Только русские и англииcke буквы, пробелы
   email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' # Email
   
   # Валидация ввода
   # Имя
   if not name:
      return False, 'empty name'
   
   name = name.strip()
   
   if len(name) < 2 or len(name) > 20:
      return False, 'invalid name length'
   
   if not re.match(full_name_pattern, name):
      return False, 'invalid name format'
   
   # Фамилия
   if not surname:
      return False, 'empty surname'
   
   surname = surname.strip()
   
   if len(surname) < 2 or len(surname) > 20:
      return False, 'invalid surname length'
   
   if not re.match(full_name_pattern, surname):
      return False, 'invalid surname format'
   
   # Отчество
   if patronymic:
      patronymic = patronymic.strip()

      if len(patronymic) < 2 or len(patronymic) > 20:
         return False, 'invalid patronymic length'
      
      if not re.match(full_name_pattern, patronymic):
         return False, 'invalid patronymic format'

   # Email
   if not email:
      return False, 'empty email'
   
   email = email.strip()

   if len(email) < 5 or len(email) > 50:
      return False, 'invalid email length'
   
   if not re.match(email_pattern, email):
      return False, 'invalid email format'
   
   # Пароль
   if not password:
      return False, 'empty password'

   password = password.strip()

   if len(password) < 8 or len(password) > 50:
      return False, 'invalid password length'
   
   # Роль
   if role not in ['user', 'manager', 'admin']:
      return False, 'unknown role'


   with db.get_cursor() as cursor:
      # Проверяем, есть ли уже пользователь с таким email
      cursor.execute("""
      SELECT id FROM users WHERE email = %s
      """, (email,))

      row = cursor.fetchone()

      if row:
         return False, 'this email already exists'
   
   
   # Создаём пользователя
   password_hash = generate_password_hash(password)

   try:
      with db.get_cursor(commit=True) as cursor:
         cursor.execute("""
         INSERT INTO client (name, surname, patronymic)
         VALUES (%s, %s, %s)
         RETURNING id
         """, (name, surname, patronymic))

         client_id = cursor.fetchone()[0]

         cursor.execute("""
         INSERT INTO users (id, role, email, password_hash)
         VALUES (%s, %s, %s, %s)
         """, (client_id, role, email, password_hash))

         user_id = cursor.lastrowid

         return user_id, ''
   except Exception as e:
      return False, f'unknown error: {str(e)}'


def login_user(email, password):
   """Авторизация пользователя.

   Args:
      email (str): Email.
      password (str): Пароль.

   Returns:
      list: Данные пользователя (или None, если авторизация не удалась)
      str: Текст ошибки (если авторизация не удалась)

   """
   
   if not email:
      return None, 'empty email'

   email = email.strip()

   if not password:
      return None, 'empty password'
   
   password = password.strip()

   with db.get_cursor(as_dict=True) as cursor:
      cursor.execute("""
      SELECT
         u.id AS id,
         c.name AS name,
         c.surname AS surname,
         c.patronymic AS patronymic,
         u.email AS email,
         u.password_hash AS password_hash,
         u.role AS role
      FROM users u
      JOIN client c
      ON u.id = c.id
      WHERE u.email = %s
      """, (email,))

      row = cursor.fetchone()

      if not row:
         return None, 'email or password is incorrect'
      
      if not check_password_hash(row['password_hash'], password):
         return None, 'email or password is incorrect'

      return User(row['id'], row['name'], row['surname'], row['patronymic'], row['email'], row['password_hash'], row['role']), ''
