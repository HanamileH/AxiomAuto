import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Загружаем переменные окружения
load_dotenv()

# ===== База данных ===== #
def init_db():
   """Инициализация базы данных
   """
   global conn
   
   conn = psycopg2.connect(
      host=os.getenv("DB_HOSTNAME"),
      database=os.getenv("DB_DATABASE"),
      user=os.getenv("DB_USERNAME"),
      password=os.getenv("DB_PASSWORD"),
      client_encoding="UTF-8"
   )
   
   cursor = conn.cursor()
   
   with open('./sql/init_schema.sql', 'r') as file:
      cursor.execute(file.read())
      
   conn.commit()
   
   # Если таблицы пустые, заполним их тестовыми данными
   cursor.execute("SELECT COUNT(*) FROM model")
   count = cursor.fetchone()[0]

   if count == 0:
      with open('./sql/fill_tables.sql', 'r') as file:
         cursor.execute(file.read())

      conn.commit()
   
   cursor.close()


# ===== Методы для CRUD ===== #
ENGINE_TYPES = {
   "petrol": "Бензин",
   "diesel": "Дизель",
   "electric": "Электро",
   "hybrid": "Гибрид"
}

TRANSMISSION_TYPES = {
   "manual": "Механическая",
   "automatic": "Автоматическая",
   "variator": "Вариатор",
   "robotic": "Роботизированная"
}


def get_catalog():
   """Получить каталог моделей
   Returns:
      list: Массив моделей
   """
   
   cursor = conn.cursor(cursor_factory=RealDictCursor)
   cursor.execute("""
   SELECT
      b.name AS brand,
      m.name AS name,
      m.id AS id,
      m.year AS year,
      MIN(mc.price) AS min_price,
      m.engine_type AS engine_type,
      m.transmission AS transmission
   FROM
      model m
   JOIN brand b ON m.brand_id = b.id
   JOIN model_configuration mc ON m.id = mc.model_id
   GROUP BY m.id, b.name, m.name;        
   """)
   
   rows = cursor.fetchall()

   cursor.close()
   
   result = list()
   
   for row in rows:
      row["engine_type"] = ENGINE_TYPES[row["engine_type"]]
      row["transmission"] = TRANSMISSION_TYPES[row["transmission"]]
      row["min_price"] = f"{int(row["min_price"]):,}".replace(",", " ")

      result.append(row)

   return rows

   
def get_model_data(model_id):
   """Получить данных модели по ID
   Args:
      model_id (int): ID модели
   Returns:
      dict: Модель (или None, если не найдена)
   """
   
   cursor = conn.cursor(cursor_factory=RealDictCursor)
   cursor.execute("""
   SELECT
      b.name AS brand,
      m.name AS name,
      m.year AS year,
      m.engine_type AS engine_type,
      m.engine_volume AS engine_volume,
      m.engine_power AS engine_power,
      m.transmission AS transmission,
      mc.price AS min_price,
      mc.description AS description
   FROM model m
   JOIN brand b ON m.brand_id = b.id
   JOIN model_configuration mc ON m.id = mc.model_id
   WHERE m.id = %s ORDER BY mc.price LIMIT 1;
   """, (model_id,))
   row = cursor.fetchone()

   cursor.close()

   result = dict(row)
   
   if result is None:
      return None

   result["engine_type"] = ENGINE_TYPES[result["engine_type"]]
   result["transmission"] = TRANSMISSION_TYPES[result["transmission"]]
   result["min_price"] = f"{int(result["min_price"]):,}".replace(",", " ")

   return result
   