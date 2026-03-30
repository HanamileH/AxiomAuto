from .connection import db

ENGINE_TYPES = {
    "petrol": "Бензин",
    "diesel": "Дизель",
    "electric": "Электро",
    "hybrid": "Гибрид",
}

TRANSMISSION_TYPES = {
    "manual": "Механическая",
    "automatic": "Автоматическая",
    "variator": "Вариатор",
    "robotic": "Роботизированная",
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
]

STATS_TYPES = [
    {
        "name": "Продажи по маркам",
        "table": "brand_sales_view",
        "columns": {
            "brand": "Производитель",
            "count": "Продаж"
        },
    },
    {
        "name": "Продажи по цветам",
        "table": "color_sales_view",
        "columns": {
            "color": "Цвет",
            "count": "Продаж"
        },
    },
    {
        "name": "Продажи по типам кузовов",
        "table": "body_type_sales_view",
        "columns": {
            "body_type": "Тип кузова",
            "count": "Продаж"
        },
    },
    {
        "name": "Эффективность менеджеров",
        "table": "manager_perfomance_view",
        "columns": {
            "name": "Имя",
            "surname": "Фамилия",
            "patronymic": "Отчество",
            "sales": "Оформлено продаж",
            "deliveries": "Оформлено доставок",
        },
    },
]


def _format_catalog_row(row):
    row["engine_type"] = ENGINE_TYPES[row["engine_type"]]
    row["transmission"] = TRANSMISSION_TYPES[row["transmission"]]
    row["price_formatted"] = f"{int(row['price']):,}".replace(",", " ")

    return row


def get_catalog(filters=None):
    """Получить каталог моделей
    Returns:
        list: Массив моделей
    """

    filters = filters or {}

    query = """
    SELECT
        m.id AS id,
        b.name AS brand,
        m.name AS model,
        m.image_path AS image_path,
        m.price AS price,
        m.year AS year,
        m.engine_type AS engine_type,
        m.engine_volume AS engine_volume,
        m.engine_power AS engine_power,
        m.transmission AS transmission
    FROM model m
    JOIN brand b ON m.brand_id = b.id
    """

    conditions = []
    params = []

    if filters.get("brand"):
        conditions.append("LOWER(b.name) LIKE LOWER(%s)")
        params.append(f"%{filters['brand']}%")

    if filters.get("model"):
        conditions.append("LOWER(m.name) LIKE LOWER(%s)")
        params.append(f"%{filters['model']}%")

    if filters.get("year_from") is not None:
        conditions.append("m.year >= %s")
        params.append(filters["year_from"])

    if filters.get("year_to") is not None:
        conditions.append("m.year <= %s")
        params.append(filters["year_to"])

    if filters.get("price_from") is not None:
        conditions.append("m.price >= %s")
        params.append(filters["price_from"])

    if filters.get("price_to") is not None:
        conditions.append("m.price <= %s")
        params.append(filters["price_to"])

    if filters.get("engine_type"):
        conditions.append("m.engine_type = %s")
        params.append(filters["engine_type"])

    if filters.get("transmission"):
        conditions.append("m.transmission = %s")
        params.append(filters["transmission"])

    if filters.get("engine_volume_min") is not None:
        conditions.append("m.engine_volume >= %s")
        params.append(filters["engine_volume_min"])

    if filters.get("engine_power_min") is not None:
        conditions.append("m.engine_power >= %s")
        params.append(filters["engine_power_min"])

    conditions.append("""
        EXISTS (
            SELECT 1
            FROM car c
            LEFT JOIN sale s ON c.id = s.car_id
            WHERE c.model_id = m.id
            AND s.id IS NULL  -- Car has no sale record (not sold/not reserved)
        )                
    """)

    query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY brand, model;"

    with db.get_cursor(as_dict=True) as cursor:
        cursor.execute(query, tuple(params))

        rows = cursor.fetchall()

        return [_format_catalog_row(row) for row in rows]


def get_model_data(model_id):
    """Получить данных модели по ID
    Args:
        model_id (int): ID модели
    Returns:
        dict: Модель (или None, если не найдена)
    """

    with db.get_cursor(as_dict=True) as cursor:
        cursor.execute(
        """
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
        """,
            (model_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        result = dict(row)

        result["engine_type"] = ENGINE_TYPES[result["engine_type"]]
        result["transmission"] = TRANSMISSION_TYPES[result["transmission"]]
        result["price"] = f"{int(result['price']):,}".replace(",", " ")

        # Получаем список доступных цветов
        cursor.execute(
        """
            WITH model_colors AS (
                -- Get distinct colors that exist for the specified model
                SELECT DISTINCT
                    c.id AS color_id,
                    c.name AS color_name,
                    c.hex_code
                FROM color c
                WHERE EXISTS (
                    SELECT 1 
                    FROM car car_instance
                    WHERE car_instance.model_id = %s
                    AND car_instance.color_id = c.id
                )
            ),
            color_availability AS (
                -- For each color, check if there's any unsold car
                SELECT 
                    mc.color_id,
                    mc.color_name,
                    mc.hex_code,
                    EXISTS (
                        SELECT 1
                        FROM car car_instance
                        LEFT JOIN sale s ON car_instance.id = s.car_id
                        WHERE car_instance.model_id = %s
                        AND car_instance.color_id = mc.color_id
                        AND s.id IS NULL  -- No sale record means not sold/not reserved
                    ) AS available_for_sale
                FROM model_colors mc
            )
            SELECT 
                color_id AS id,
                color_name AS color,
                hex_code,
                available_for_sale AS is_available_for_sale
            FROM color_availability
            ORDER BY color_name;
        """,
            (model_id, model_id)
        )

        # Добавляем информацию о цветах
        colors = cursor.fetchall()
        colors_data = [dict(row) for row in colors]

        result["colors"] = colors_data

        return result


def get_statistics(stats_id):
    """Получить данные для статистики
    Args:
        stats_id (int): ID статистики
    Returns:
        dict: Статистика (или None, если не найдена)
    """

    with db.get_cursor(as_dict=True) as cursor:
        if stats_id is None:
            return None

        stats_id = int(stats_id)

        if stats_id < 0 or stats_id >= len(STATS_TYPES):
            return None

        stats_info = STATS_TYPES[stats_id]

        # Получаем данные из представления
        columns_name = list(stats_info["columns"].keys())

        cursor.execute(f"SELECT {', '.join(columns_name)} FROM {stats_info['table']};")

        rows = cursor.fetchall()

        # Возвращаем данные
        return {
            "name": stats_info["name"],
            "columns": columns_name,
            "columns_ru": list(stats_info["columns"].values()),
            "rows": rows,
        }
