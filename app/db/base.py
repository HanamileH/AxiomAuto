from .connection import db

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

ENTITIES_TYPES = [
   {
      "tab_name": "brands",
      "ru_name": "Марки",
   },
   {
      "tab_name": "body_types",
      "ru_name": "Типы кузова",
   },
   {
      "tab_name": "models",
      "ru_name": "Модели",
   },
   {
      "tab_name": "colors",
      "ru_name": "Цвета",
   },
   {
      "tab_name": "cars",
      "ru_name": "Автомобили",
   },
   {
      "tab_name": "users",
      "ru_name": "Пользователи",
   },
   {
      "tab_name": "sales",
      "ru_name": "Заказы",
   },
   {
      "tab_name": "payments",
      "ru_name": "Оплаты",
   },
   {
      "tab_name": "statistics",
      "ru_name": "Статистика",
   }
]


def get_catalog():
    """Получить каталог моделей
    Returns:
        list: Массив моделей
    """

    with db.get_cursor(as_dict=True) as cursor:
            cursor.execute("""
            SELECT
               m.id AS id,
               b.name AS brand,
               m.name AS model,
               m.image_path AS image_path,
               m.price AS price,
               m.year AS year,
               m.engine_type AS engine_type,
               m.transmission AS transmission
            FROM model m
            JOIN brand b
            ON m.brand_id = b.id;
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                row["engine_type"] = ENGINE_TYPES[row["engine_type"]]
                row["transmission"] = TRANSMISSION_TYPES[row["transmission"]]
                row["price"] = f"{int(row["price"]):,}".replace(",", " ")

            return rows
    

def get_model_data(model_id):
    """Получить данных модели по ID
    Args:
        model_id (int): ID модели
    Returns:
        dict: Модель (или None, если не найдена)
    """
   
    with db.get_cursor(as_dict=True) as cursor:
        cursor.execute("""
         SELECT
            b.name AS brand,
            m.name AS model,
            m.description AS description,
            m.image_path AS image_path,
            m.price AS price,
            m.year AS year,
            bt.name AS body_type,
            m.engine_type AS engine_type,
            m.engine_volume AS engine_volume,
            m.engine_power AS engine_power,
            
            m.transmission AS transmission
         FROM model m
         JOIN brand b
         ON m.brand_id = b.id
         JOIN body_type bt
         ON m.body_type = bt.id
         WHERE m.id = %s;
        """, (model_id,))

        row = cursor.fetchone()
        
        if row is None:
            return None
        
        result = dict(row)

        result["engine_type"] = ENGINE_TYPES[result["engine_type"]]
        result["transmission"] = TRANSMISSION_TYPES[result["transmission"]]
        result["price"] = f"{int(result["price"]):,}".replace(",", " ")

        return result
   