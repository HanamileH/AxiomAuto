from .connection import db

# CRUD-операции над записями таблицы brand
class Brand:
   @staticmethod
   def get_all():
      """Получение всех записей
      Returns:
         list: Массив записей
      """
      try:
         with db.get_cursor(as_dict=True) as cursor:
            cursor.execute("SELECT id AS id, name AS name FROM brand;")
            rows = cursor.fetchall()
            return rows, ''
      except Exception as e:
         return None, str(e)
      

   @staticmethod
   def get_by_id(id):
      """Получение записи по ID
      Args:
         id (int): ID записи
      Returns:
         dict: Запись (или None, если не найдена)
      """
      try:
         with db.get_cursor(as_dict=True) as cursor:
            cursor.execute("SELECT id AS id, name AS name FROM brand WHERE id = %s;", (id,))
            row = cursor.fetchone()
            return row, ''
      except Exception as e:
         return None, str(e)


   @staticmethod
   def create(name):
      """Создание записи
      Args:
         name (str): Название
      Returns:
         int: ID созданной записи (или None, если ошибка)
         String: Сообщение об ошибке (или '', если нет ошибок)
      """
      try:
         with db.get_cursor(commit=True) as cursor:
            # Проверяем, что данное имя ещё не используется
            cursor.execute("SELECT id FROM brand WHERE name = %s;", (name,))
            row = cursor.fetchone()

            if row:
               return None, 'Это название уже используется'

            # Выполняем вставку
            cursor.execute("INSERT INTO brand (name) VALUES (%s) RETURNING id", (name,))

            # Возвращаем id новой записи
            id = cursor.fetchone()[0]
            return id, ''
      except Exception as e:
         return None, f'Ошибка базы данных: {str(e)}'


   @staticmethod
   def delete(id):
      """Удаление записи
      Args:
         id (int): ID записи
      Returns:
         bool: статус удаления (True если успешно)
         String: Сообщение об ошибке (или '', если нет ошибок)
      """
      try:
         with db.get_cursor(commit=True) as cursor:
            # Проверяем, что запись существует
            cursor.execute("SELECT id FROM brand WHERE id = %s;", (id,))
            row = cursor.fetchone()

            if row is None:
               return False, 'Запись не существует'

            # Проверяем отсутствие зависимых записей
            cursor.execute("SELECT id FROM model WHERE brand_id = %s;", (id,))
            row = cursor.fetchone()

            if row:
               return False, 'Есть зависимые записи (модели). Удаление невозможно'

            # Выполняем удаление
            cursor.execute("DELETE FROM brand WHERE id = %s;", (id,))
            return True, ''
      except Exception as e:
         return False, f'Ошибка базы данных: {str(e)}'
      
      
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
      try:
         with db.get_cursor(commit=True) as cursor:
            # Проверяем, что запись существует
            cursor.execute("SELECT id FROM brand WHERE id = %s;", (id,))
            row = cursor.fetchone()

            if row is None:
               return False, 'Запись не существует'

            # Проверяем, что данное имя ещё не используется
            cursor.execute("SELECT id FROM brand WHERE name = %s AND id != %s;", (name, id))
            row = cursor.fetchone()

            if row:
               return False, 'Это название уже используется'

            # Выполняем обновление
            cursor.execute("UPDATE brand SET name = %s WHERE id = %s;", (name, id))
            return True, ''
      except Exception as e:
         return False, f'Ошибка базы данных: {str(e)}'