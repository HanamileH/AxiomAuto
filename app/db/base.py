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
      "table_name": "brand",
      "tab_name": "brands",
      "ru_name": "Марки",
      "ru_add": "Добавить марку",
      "ru_list": "Список марок",
   },
   {
      "table_name": "model",
      "tab_name": "models",
      "ru_name": "Модели",
      "ru_add": "Добавить модель",
      "ru_list": "Список моделей"
   },
   {
      "table_name": "model_configuration",
      "tab_name": "configurations",
      "ru_name": "Комплектации",
      "ru_add": "Добавить комплектацию",
      "ru_list": "Список комплектаций"
   },
   {
      "table_name": "color",
      "tab_name": "colors",
      "ru_name": "Цвета",
      "ru_add": "Добавить цвет",
      "ru_list": "Список цветов"
   },
   {
      "table_name": "car",
      "tab_name": "cars",
      "ru_name": "Автомобили",
      "ru_add": "Добавить автомобиль",
      "ru_list": "Список автомобилей"
   },
   {
      "table_name": "users",
      "tab_name": "users",
      "ru_name": "Пользователи",
      "ru_add": "Добавить пользователя",
      "ru_list": "Список пользователей"
   },
   {
      "table_name": "car_sale",
      "tab_name": "sales",
      "ru_name": "Заказы",
      "ru_add": "Добавить заказ",
      "ru_list": "Список заказов"
   },
   {
      "table_name": None,
      "tab_name": "statistics",
      "ru_name": "Статистика",
      "ru_add": None,
      "ru_list": "Статистика"
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
                b.name AS brand,
                m.name AS name,
                m.image_path AS image_path,
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
            
            for row in rows:
                row["engine_type"] = ENGINE_TYPES[row["engine_type"]]
                row["transmission"] = TRANSMISSION_TYPES[row["transmission"]]
                row["min_price"] = f"{int(row["min_price"]):,}".replace(",", " ")

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
            m.name AS name,
            m.year AS year,
            m.image_path AS image_path,
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
        
        if row is None:
            return None
        
        result = dict(row)

        result["engine_type"] = ENGINE_TYPES[result["engine_type"]]
        result["transmission"] = TRANSMISSION_TYPES[result["transmission"]]
        result["min_price"] = f"{int(result["min_price"]):,}".replace(",", " ")

        return result
   