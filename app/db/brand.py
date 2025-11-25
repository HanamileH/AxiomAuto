from .connection import db

# CRUD-операции над записями таблицы brand
class Brand:
   @staticmethod
   def get_all():
      """Получение всех записей
      Returns:
         list: Массив записей
      """
      with db.get_cursor(as_dict=True) as cursor:
         cursor.execute("SELECT id AS id, name AS name FROM brand;")

         rows = cursor.fetchall()

         return rows
      

   @staticmethod
   def get_by_id(id):
      """Получение записи по ID
      Args:
         id (int): ID записи
      Returns:
         dict: Запись (или None, если не найдена)
      """

      with db.get_cursor(as_dict=True) as cursor:
         cursor.execute("SELECT id AS id, name AS name FROM brand WHERE id = %s;", (id,))

         row = cursor.fetchone()

         if row is None:
            return None

         return row
         

   @staticmethod
   def create(name):
      """Создание записи
      Args:
         name (str): Название
      Returns:
         int: ID созданной записи (или None, если ошибка)
         String: Сообщение об ошибке (или '', если нет ошибок)
      """

      with db.get_cursor() as cursor:
         # Проверяем, что данное имя ещё не используется
         cursor.execute("SELECT id FROM brand WHERE name = %s;", (name,))

         row = cursor.fetchone()

         if row:
            return None, 'this name is already taken'

         # Выполняем вставку
         cursor.execute("INSERT INTO brand (name) VALUES (%s);", (name,))

         id = cursor.lastrowid

         return id, ''
      return None, 'Unknown error'


   @staticmethod
   def delete(id):
      """Удаление записи
      Args:
         id (int): ID записи
      Returns:
         bool: статус удаления (True если успешно)
         String: Сообщение об ошибке (или '', если нет ошибок)
      """

      with db.get_cursor() as cursor:
         # Проверяем, что запись существует
         cursor.execute("SELECT id FROM brand WHERE id = %s;", (id,))

         row = cursor.fetchone()

         if row is None:
            return False, 'this record does not exist'

         # Проверяем отсутствие зависимых записей
         cursor.execute("SELECT id FROM model WHERE brand_id = %s;", (id,))

         row = cursor.fetchone()

         if row:
            return False, 'this record has dependent records'

         # Выполняем удаление
         cursor.execute("DELETE FROM brand WHERE id = %s;", (id,))

         return True, ''
      return False, 'Unknown error'
      

   @staticmethod
   def update(id, name):
      """Обновление записи
      Args:
         id (int): ID записи
         name (str): Новое название
      Returns:
         bool: статус обновления (True если успешно)
         String: Сообщение об ошибке (или '', если нет ошибок)
      """

      with db.get_cursor() as cursor:
         # Проверяем, что запись существует
         cursor.execute("SELECT id FROM brand WHERE id = %s;", (id,))

         row = cursor.fetchone()

         if row is None:
            return False, 'this record does not exist'

         # Проверяем, что данное имя ещё не используется
         cursor.execute("SELECT id FROM brand WHERE name = %s;", (name,))

         row = cursor.fetchone()

         if row:
            return False, 'this name is already taken'

         # Выполняем обновление
         cursor.execute("UPDATE brand SET name = %s WHERE id = %s;", (name, id,))

         return True, ''
      return False, 'Unknown error'