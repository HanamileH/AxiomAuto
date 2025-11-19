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
   
   """
   # Валидация ввода
   # Имя
   if not name:
      return False
   
   name = name.strip()
   
   if len(name) < 2 or len(name) > 20:
      return False
   
   # Фамилия
   if not surname:
      return False
   
   surname = surname.strip()
   
   if len(surname) < 2 or len(surname) > 20:
      return False
   
   # Отчество
   if patronymic:
      patronymic = patronymic.strip()

      if len(patronymic) < 2 or len(patronymic) > 20:
         return False
   
   # Номер телефона
   if not phone:
      return False
   
   phone = phone.strip()
   phone = phone.replace(" ", "").replace("-","").replace("(", "").replace(")", "")
   
   if phone.startswith("8"):
      phone = "+7" + phone[1:]
   
   if len(phone) != 12:
      return False
   
   # Email
   if not email:
      return False
   
   email = email.strip()

   if len(email) < 5 or len(email) > 50:
      return False
   
   if not '@' in email:
      return False
   
   # Пароль
   if not password:
      return False

   password = password.strip()

   if len(password) < 8:
      return False
   
   # Роль
   if role not in ['user', 'manager', 'admin']:
      return False
   
   # Создаём пользователя
   password_hash = generate_password_hash(password)

   try:
      with db.get_cursor(commit=True) as cursor:
         cursor.execute("""
         INSERT INTO users (name, surname, patronymic, phone, email, password_hash, role)
         VALUES (%s, %s, %s, %s, %s, %s, %s)
         """, (name, surname, patronymic, phone, email, password_hash, role))

         user_id = cursor.lastrowid

         return user_id
   except Exception:
      return False
   

def login_user(email, password):
   """Авторизация пользователя.

   Args:
      email (str): Email.
      password (str): Пароль.

   Returns:
      list: Данные пользователя (или None, если авторизация не удалась)

   """
   
   if not email:
      return None

   email = email.strip()

   if not password:
      return None
   
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
         return None
      
      if not check_password_hash(row['password_hash'], password):
         return None

      return User(row['id'], row['name'], row['surname'], row['patronymic'], row['phone'], row['email'], row['password_hash'], row['role'])
