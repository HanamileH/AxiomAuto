import re
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .connection import db


class User(UserMixin):
   def __init__(self, id, name, surname, patronymic, phone, email, password_hash, role='user'):
      self.id = id
      self.name = name
      self.surname = surname
      self.patronymic = patronymic
      self.phone = phone
      self.email = email
      self.password_hash = password_hash
      self.role = role


   @staticmethod
   def get_by_id(user_id):
      with db.get_cursor() as cursor:
         cursor.execute("""
         SELECT
            id,
            name,
            surname,
            patronymic,
            phone,
            email,
            password_hash,
            role
         FROM
            users
         WHERE id = %s            
         """, (user_id, ))

         row = cursor.fetchone()

         if row:
            return User(*row)
         return None


def register_user(name, surname, patronymic, phone, email, password, role='user'):
   """Регистрация нового пользователя.

   Args:
      name (str): Имя.
      surname (str): Фамилия.
      patronymic (str): Отчество.
      phone (str): Номер телефона.
      email (str): Email.
      password (str): Пароль.
      role (str): Роль пользователя (По умолчанию 'user').

   Returns:
      Int: ID пользователя (или False, если добавление не удалось)
      String: Текст ошибки (если добавление не удалось)
   
   """
   
   # Регулярные выражения для валидации
   full_name_pattern = r'^[a-zA-Zа-яёА-ЯЁ\s]+$' # Только русские и англииcke буквы, пробелы
   phone_pattern = r'^\+7\d{10}$' # Номер телефона в формате +7xxxxxxxxxx
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
   
   # Номер телефона
   if not phone:
      return False, 'empty phone'
   
   phone = phone.strip()
   phone = phone.replace(" ", "").replace("-","").replace("(", "").replace(")", "")
   
   if phone.startswith("8"):
      phone = "+7" + phone[1:]
   
   if len(phone) != 12:
      return False, 'invalid phone length'
   
   if not re.match(phone_pattern, phone):
      return False, 'invalid phone format'
   
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
      
      # Проверяем, есть ли уже пользователь с таким номером телефона\
      cursor.execute("""
         SELECT id FROM users WHERE phone = %s
      """, (phone,))

      row = cursor.fetchone()

      if row:
         return False, 'this phone already exists'
   
   
   # Создаём пользователя
   password_hash = generate_password_hash(password)

   try:
      with db.get_cursor(commit=True) as cursor:
         cursor.execute("""
         INSERT INTO users (name, surname, patronymic, phone, email, password_hash, role)
         VALUES (%s, %s, %s, %s, %s, %s, %s)
         """, (name, surname, patronymic, phone, email, password_hash, role))

         user_id = cursor.lastrowid

         return user_id, ''
   except Exception:
      return False, 'unknown error'


# Список всех ошибок при регистрации:
# 'empty name'
# 'invalid name length'
# 'invalid name format'
# 'empty surname'
# 'invalid surname length'
# 'invalid surname format'
# 'empty patronymic' (не используется, допускается пустое отчество)
# 'invalid patronymic length'
# 'invalid patronymic format'
# 'empty phone'
# 'invalid phone length'
# 'invalid phone format'
# 'empty email'
# 'invalid email length'
# 'invalid email format'
# 'empty password'
# 'invalid password length'
# 'unknown role'
# 'this email already exists'
# 'this phone already exists'
# 'unknown error'
#
# Список всех ошибок при авторизации:
# 'empty email'
# 'empty password'
# 'email or password is incorrect'
# 'unknown error'

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
         id,
         name,
         surname,
         patronymic,
         phone,
         email,
         password_hash,
         role
      FROM users
      WHERE email = %s
      """, (email,))

      row = cursor.fetchone()

      if not row:
         return None, 'email or password is incorrect'
      
      if not check_password_hash(row['password_hash'], password):
         return None, 'email or password is incorrect'

      return User(row['id'], row['name'], row['surname'], row['patronymic'], row['phone'], row['email'], row['password_hash'], row['role']), ''
