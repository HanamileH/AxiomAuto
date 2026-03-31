from .connection import db
import re
import hashlib
from werkzeug.security import generate_password_hash
from .user import DataEncryption


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
                cursor.execute("""
                    WITH model_stats AS (
                        SELECT 
                            m.brand_id,
                            COUNT(DISTINCT m.id) AS total_models,
                            COUNT(c.id) AS total_cars,
                            COUNT(s.id) AS sold_cars
                        FROM model m
                        LEFT JOIN car c ON c.model_id = m.id
                        LEFT JOIN sale s ON s.car_id = c.id
                        GROUP BY m.brand_id
                    )
                    SELECT 
                        b.id AS id,
                        b.name AS name,
                        COALESCE(ms.sold_cars, 0) AS sold_cars,
                        COALESCE(ms.total_cars - ms.sold_cars, 0) AS available_cars
                    FROM brand b
                    LEFT JOIN model_stats ms ON ms.brand_id = b.id
                    ORDER BY b.name;
                """)
                rows = cursor.fetchall()
                return rows, ""
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
                cursor.execute(
                    "SELECT id AS id, name AS name FROM brand WHERE id = %s;", (id,)
                )
                row = cursor.fetchone()
                return row, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                    return None, "this name is already taken"

                # Выполняем вставку
                cursor.execute(
                    "INSERT INTO brand (name) VALUES (%s) RETURNING id", (name,)
                )

                # Возвращаем id новой записи
                id = cursor.fetchone()[0]
                return id, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                    return False, "this record does not exist"

                # Проверяем отсутствие зависимых записей
                cursor.execute("SELECT id FROM model WHERE brand_id = %s;", (id,))
                row = cursor.fetchone()

                if row:
                    return False, "this record has dependent records"

                # Выполняем удаление
                cursor.execute("DELETE FROM brand WHERE id = %s;", (id,))
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"

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
                    return False, "this record does not exist"

                # Проверяем, что данное имя ещё не используется
                cursor.execute(
                    "SELECT id FROM brand WHERE name = %s AND id != %s;", (name, id)
                )
                row = cursor.fetchone()

                if row:
                    return False, "this name is already taken"

                # Выполняем обновление
                cursor.execute("UPDATE brand SET name = %s WHERE id = %s;", (name, id))
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"


# CRUD-операции над записями таблицы body_type
class Body_type:
    @staticmethod
    def get_all():
        """Получение всех записей
        Returns:
           list: Массив записей
        """
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute("SELECT id AS id, name AS name FROM body_type ORDER BY name;")
                rows = cursor.fetchall()
                return rows, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                cursor.execute(
                    "SELECT id AS id, name AS name FROM body_type WHERE id = %s;", (id,)
                )
                row = cursor.fetchone()
                return row, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                cursor.execute("SELECT id FROM body_type WHERE name = %s;", (name,))
                row = cursor.fetchone()

                if row:
                    return None, "this name is already taken"

                # Выполняем вставку
                cursor.execute(
                    "INSERT INTO body_type (name) VALUES (%s) RETURNING id", (name,)
                )

                # Возвращаем id новой записи
                id = cursor.fetchone()[0]
                return id, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                cursor.execute("SELECT id FROM body_type WHERE id = %s;", (id,))
                row = cursor.fetchone()

                if row is None:
                    return False, "this record does not exist"

                # Проверяем отсутствие зависимых записей
                cursor.execute("SELECT id FROM model WHERE body_type = %s;", (id,))
                row = cursor.fetchone()

                if row:
                    return False, "this record has dependent records"

                # Выполняем удаление
                cursor.execute("DELETE FROM body_type WHERE id = %s;", (id,))
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"

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
                cursor.execute("SELECT id FROM body_type WHERE id = %s;", (id,))
                row = cursor.fetchone()

                if row is None:
                    return False, "this record does not exist"

                # Проверяем, что данное имя ещё не используется
                cursor.execute(
                    "SELECT id FROM body_type WHERE name = %s AND id != %s;", (name, id)
                )
                row = cursor.fetchone()

                if row:
                    return False, "this name is already taken"

                # Выполняем обновление
                cursor.execute(
                    "UPDATE body_type SET name = %s WHERE id = %s;", (name, id)
                )
                return True, ""

        except Exception as e:
            return False, f"server error: {str(e)}"


# CRUD-операции над записями таблицы color
class Color:
    @staticmethod
    def get_all():
        """Получение всех записей
        Returns:
           list: Массив записей
        """
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT id AS id, name AS name, hex_code AS hex_code FROM color ORDER BY name;"
                )
                rows = cursor.fetchall()
                return rows, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                cursor.execute(
                    "SELECT id AS id, name AS name, hex_code AS hex_code FROM color WHERE id = %s;",
                    (id,),
                )
                row = cursor.fetchone()
                return row, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def create(name, hex_code):
        """Создание записи
        Args:
           name (str): Название
           hex_code (str): HEX-код
        Returns:
           int: ID созданной записи (или None, если ошибка)
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Проверяем, что данное имя ещё не используется
                cursor.execute("SELECT id FROM color WHERE name = %s;", (name,))
                row = cursor.fetchone()

                if row:
                    return None, "this name is already taken"

                # Выполняем вставку
                cursor.execute(
                    "INSERT INTO color (name, hex_code) VALUES (%s, %s) RETURNING id",
                    (name, hex_code),
                )

                # Возвращаем id новой записи
                id = cursor.fetchone()[0]
                return id, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

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
                cursor.execute("SELECT id FROM color WHERE id = %s;", (id,))
                row = cursor.fetchone()
                if row is None:
                    return False, "this record does not exist"

                # Выполняем удаление
                cursor.execute("DELETE FROM color WHERE id = %s;", (id,))
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"

    @staticmethod
    def update(id, name, hex_code):
        """Обновление записи
        Args:
           id (int): ID записи
           name (str): Новое название
           hex_code (str): Новый HEX-код
        Returns:
           bool: статус обновления (True если успешно)
           String: Сообщение об ошибке (или '', если нет ошибок)
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Проверяем, что запись существует
                cursor.execute("SELECT id FROM color WHERE id = %s;", (id,))
                row = cursor.fetchone()

                if row is None:
                    return False, "this record does not exist"

                updates = []
                params = []

                if name:
                    updates.append("name = %s")
                    params.append(name)

                if hex_code:
                    updates.append("hex_code = %s")
                    params.append(hex_code)

                params.append(id)

                # Проверяем, что имя не занято
                if name:
                    cursor.execute(
                        "SELECT id FROM color WHERE name = %s AND id != %s;", (name, id)
                    )
                    row = cursor.fetchone()

                    if row:
                        return False, "this name is already taken"

                # Выполняем обновление
                cursor.execute(
                    f"UPDATE color SET {', '.join(updates)} WHERE id = %s;", params
                )
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"


# CRUD-операции над записями таблицы Model
class Model:
    @staticmethod
    def get_all():
        """Получение всех записей
        Returns:
           list: Массив записей
        """
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    """
                    WITH car_stats AS (
                        SELECT 
                            c.model_id,
                            COUNT(c.id) AS total_cars,
                            COUNT(s.id) AS sold_cars
                        FROM car c
                        LEFT JOIN sale s ON s.car_id = c.id
                        GROUP BY c.model_id
                    )
                    SELECT
                        m.id AS id,
                        m.name AS model,
                        m.description AS description,
                        m.year AS year,
                        m.price AS price,
                        m.engine_type AS engine_type,
                        m.engine_power AS engine_power,
                        m.engine_volume AS engine_volume,
                        m.transmission AS transmission,
                        m.brand_id AS brand_id,
                        m.body_type AS body_type_id,
                        b.name AS brand,
                        bt.name AS body_type,
                        COALESCE(cs.sold_cars, 0) AS sold_cars,
                        COALESCE(cs.total_cars - cs.sold_cars, 0) AS available_cars
                    FROM model m
                    JOIN brand b ON b.id = m.brand_id
                    JOIN body_type bt ON bt.id = m.body_type
                    LEFT JOIN car_stats cs ON cs.model_id = m.id
                    ORDER BY brand, model;      
                    """
                )
                rows = cursor.fetchall()
                return rows, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def get_by_id(id):
        """Получение записи по ID
        Args:
           id (int): ID записи
        Returns:
           dict: Запись
           String: Сообщение об ошибке (или '', если нет ошибок)
        """
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    """
              SELECT
               m.id AS id,
               m.name AS model,
               m.description AS description,
               m.price AS price,
               m.year AS year,
               m.engine_type AS engine_type,
               m.engine_power AS engine_power,
               m.engine_volume AS engine_volume,
               m.transmission AS transmission,
               m.brand_id AS brand_id,
               m.body_type AS body_type_id,
               b.name AS brand,
               bt.name AS body_type
            FROM model m
            JOIN brand b ON b.id = m.brand_id
            JOIN body_type bt ON bt.id = m.body_type
            WHERE m.id = %s;
            """,
                    (id,),
                )
                row = cursor.fetchone()
                return row, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def create(
        name,
        description,
        price,
        year,
        engine_type,
        engine_power,
        engine_volume,
        transmission,
        brand_id,
        body_type_id,
        image_path,
    ):
        """Создание записи
        Args:
           name (str): Название
           description (str): Описание
           price (int): Цена
           year (int): Год выпуска
           engine_type (str): Тип двигателя
           engine_power (int): Мощность двигателя
           engine_volume (float, None): Объем двигателя (None для электродвигателей)
           transmission (str): Коробка передач
           brand_id (int): ID бренда
           body_type_id (int): ID типа кузова
        Returns:
           int: ID созданной записи (или None, если ошибка)
           String: Сообщение об ошибке (или '', если нет ошибок)
        """

        try:
            with db.get_cursor(commit=True) as cursor:
                # Проверяем, что имя не занято
                cursor.execute("SELECT id FROM model WHERE name = %s;", (name,))
                row = cursor.fetchone()

                if row:
                    return False, "this name is already taken"

                # Создаем запись
                cursor.execute(
                    """
               INSERT INTO model (name, description, price, year, engine_type, engine_power, engine_volume, transmission, brand_id, body_type, image_path)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """,
                    (
                        name,
                        description,
                        price,
                        year,
                        engine_type,
                        engine_power,
                        engine_volume,
                        transmission,
                        brand_id,
                        body_type_id,
                        image_path,
                    ),
                )

                # Возвращаем id новой записи
                id = cursor.fetchone()[0]
                return id, ""

        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def update(
        id,
        name,
        description,
        price,
        year,
        engine_type,
        engine_power,
        engine_volume,
        transmission,
        brand_id,
        body_type_id,
        image_path=None,
    ):
        """Обновление записи
        Args:
           id (int): ID записи
           name (str): Название
           description (str): Описание
           price (int): Цена
           year (int): Год выпуска
           engine_type (str): Тип двигателя
           engine_power (int): Мощность двигателя
           engine_volume (float, None): Объем двигателя (None для электродвигателей)
           transmission (str): Коробка передач
           brand_id (int): ID бренда
           body_type_id (int): ID типа кузова
        Returns:
           bool: True, если обновление прошло успешно (или False, если ошибка)
           String: Сообщение об ошибке (или '', если нет ошибок)
        """

        try:
            with db.get_cursor(commit=True) as cursor:
                # Проверяем, что запись существует
                cursor.execute("SELECT id FROM model WHERE id = %s;", (id,))
                row = cursor.fetchone()

                if not row:
                    return False, "this record does not exist"

                updates = []
                params = []

                if name:
                    # Получаем текущий ID бренда (если он не заменён)
                    if brand_id is None:
                        cursor.execute("SELECT brand_id FROM model WHERE id = %s;", (id,))
                        brand_id = cursor.fetchone()[0]

                    # Проверяем, что данное имя в этом бренде уже занято
                    cursor.execute("SELECT id FROM model WHERE name = %s AND brand_id = %s AND id != %s;", (name, brand_id, id,))
                    row = cursor.fetchone()

                    if row:
                        return False, "this name is already taken"

                    updates.append("name = %s")
                    params.append(name)

                if description:
                    updates.append("description = %s")
                    params.append(description)

                if price:
                    updates.append("price = %s")
                    params.append(price)

                if year:
                    updates.append("year = %s")
                    params.append(year)

                if engine_type:
                    updates.append("engine_type = %s")
                    params.append(engine_type)

                if engine_power:
                    updates.append("engine_power = %s")
                    params.append(engine_power)

                if engine_volume:
                    updates.append("engine_volume = %s")
                    params.append(engine_volume)
                elif engine_type == "electric":
                    updates.append("engine_volume = NULL")

                if transmission:
                    updates.append("transmission = %s")
                    params.append(transmission)

                if brand_id:
                    # Получаем текущее имя (если оно не заменено)
                    if name is None:
                        cursor.execute("SELECT name FROM model WHERE id = %s;", (id,))
                        name = cursor.fetchone()[0]

                    # Проверяем, что данное имя в этом бренде уже занято
                    cursor.execute("SELECT id FROM model WHERE name = %s AND brand_id = %s AND id != %s;", (name, brand_id, id,))
                    row = cursor.fetchone()

                    if row:
                        return False, "this name is already taken"

                    updates.append("brand_id = %s")
                    params.append(brand_id)

                if body_type_id:
                    updates.append("body_type = %s")
                    params.append(body_type_id)

                if image_path:
                    updates.append("image_path = %s")
                    params.append(image_path)

                params.append(id)

                cursor.execute(
                    f"UPDATE model SET {', '.join(updates)} WHERE id = %s;", params
                )
                return True, ""

        except Exception as e:
            return False, f"server error: {str(e)}"

    @staticmethod
    def get_image_path(id):
        """Получение пути к изображению модели по ID"""
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT image_path AS image_path FROM model WHERE id = %s;",
                    (id,),
                )
                row = cursor.fetchone()

                if row is None:
                    return None, "this record does not exist"

                return row["image_path"], ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def delete(id):
        """Удаление записи
        Args:
           id (int): ID записи
        Returns:
           bool: True, если удаление прошло успешно (или False, если ошибка)
           String: Сообщение об ошибке (или '', если нет ошибок)
        """

        try:
            with db.get_cursor(commit=True) as cursor:
                # Проверяем, что запись существует
                cursor.execute("SELECT id FROM model WHERE id = %s;", (id,))
                row = cursor.fetchone()

                if not row:
                    return False, "this record does not exist"

                # Проверяем отсутствие зависимых записей
                cursor.execute("SELECT id FROM car WHERE model_id = %s;", (id,))
                row = cursor.fetchone()

                if row:
                    return False, "this record has dependent records"

                # Удаляем запись
                cursor.execute("DELETE FROM model WHERE id = %s;", (id,))
                return True, ""

        except Exception as e:
            return False, f"server error: {str(e)}"


# CRUD-операции над записями таблицы car
class Car:
    @staticmethod
    def get_all():
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id AS id,
                        c.vin AS vin,
                        c.model_id AS model_id,
                        m.name AS model,
                        m.brand_id AS brand_id,
                        b.name AS brand,
                        c.color_id AS color_id,
                        clr.name AS color,
                        EXISTS(
                            SELECT 1 FROM sale s WHERE s.car_id = c.id
                        ) AS is_sold
                    FROM car c
                    JOIN model m ON m.id = c.model_id
                    JOIN brand b ON b.id = m.brand_id
                    JOIN color clr ON clr.id = c.color_id
                    ORDER BY b.name, m.name, c.vin;
                    """
                )
                rows = cursor.fetchall()
                return rows, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def create(model_id, color_id, vin):
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("SELECT id FROM model WHERE id = %s;", (model_id,))
                if cursor.fetchone() is None:
                    return None, "model not found"

                cursor.execute("SELECT id FROM color WHERE id = %s;", (color_id,))
                if cursor.fetchone() is None:
                    return None, "color not found"

                cursor.execute("SELECT id FROM car WHERE vin = %s;", (vin,))
                if cursor.fetchone() is not None:
                    return None, "this VIN is already taken"

                cursor.execute(
                    "INSERT INTO car (model_id, color_id, vin) VALUES (%s, %s, %s) RETURNING id;",
                    (model_id, color_id, vin),
                )
                car_id = cursor.fetchone()[0]
                return car_id, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def update(id, model_id=None, color_id=None, vin=None):
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("SELECT id FROM car WHERE id = %s;", (id,))
                if cursor.fetchone() is None:
                    return False, "this record does not exist"

                updates = []
                params = []

                if model_id is not None:
                    cursor.execute("SELECT id FROM model WHERE id = %s;", (model_id,))
                    if cursor.fetchone() is None:
                        return False, "model not found"
                    updates.append("model_id = %s")
                    params.append(model_id)

                if color_id is not None:
                    cursor.execute("SELECT id FROM color WHERE id = %s;", (color_id,))
                    if cursor.fetchone() is None:
                        return False, "color not found"
                    updates.append("color_id = %s")
                    params.append(color_id)

                if vin is not None:
                    cursor.execute("SELECT id FROM car WHERE vin = %s AND id != %s;", (vin, id))
                    if cursor.fetchone() is not None:
                        return False, "this VIN is already taken"
                    updates.append("vin = %s")
                    params.append(vin)

                if not updates:
                    return True, ""

                params.append(id)
                cursor.execute(
                    f"UPDATE car SET {', '.join(updates)} WHERE id = %s;",
                    params,
                )
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"

    @staticmethod
    def delete(id):
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("SELECT id FROM car WHERE id = %s;", (id,))
                if cursor.fetchone() is None:
                    return False, "this record does not exist"

                cursor.execute("SELECT id FROM sale WHERE car_id = %s;", (id,))
                if cursor.fetchone() is not None:
                    return False, "this record has dependent records"

                cursor.execute("DELETE FROM car WHERE id = %s;", (id,))
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"


class StaffUser:
    @staticmethod
    def get_all():
        try:
            with db.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        u.id AS id,
                        c.name AS name,
                        c.surname AS surname,
                        c.patronymic AS patronymic,
                        u.email AS email,
                        u.role AS role
                    FROM users u
                    JOIN client c ON c.id = u.id
                    ORDER BY c.surname, c.name;
                    """
                )
                rows = cursor.fetchall()

                for row in rows:
                    row["email"] = DataEncryption.decrypt(row["email"])

                return rows, ""
        except Exception as e:
            return None, f"server error: {str(e)}"

    @staticmethod
    def create(name, surname, patronymic, email, password, role):
        from .user import register_user

        user_id, error = register_user(
            name=name,
            surname=surname,
            patronymic=patronymic,
            email=email,
            password=password,
            role=role,
        )
        if not user_id:
            return None, error
        return user_id, ""

    @staticmethod
    def update(id, name, surname, patronymic, email, role, new_password=None):
        try:
            full_name_pattern = r"^[a-zA-Zа-яёА-ЯЁ\s]+$"
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

            name = (name or "").strip()
            surname = (surname or "").strip()
            patronymic = (patronymic or "").strip()
            email = (email or "").strip()

            if len(name) < 2 or len(name) > 20 or not re.match(full_name_pattern, name):
                return False, "invalid name"
            if len(surname) < 2 or len(surname) > 20 or not re.match(full_name_pattern, surname):
                return False, "invalid surname"
            if patronymic and (
                len(patronymic) < 2
                or len(patronymic) > 20
                or not re.match(full_name_pattern, patronymic)
            ):
                return False, "invalid patronymic"
            if len(email) < 5 or len(email) > 50 or not re.match(email_pattern, email):
                return False, "invalid email"
            if role not in ["user", "manager", "admin"]:
                return False, "unknown role"

            password_hash = None
            if new_password is not None and new_password.strip() != "":
                if len(new_password.strip()) < 8 or len(new_password.strip()) > 50:
                    return False, "invalid password length"
                password_hash = generate_password_hash(new_password.strip())

            encrypted_email = DataEncryption.encrypt(email)

            email_hash = hashlib.sha256(email.encode("utf-8")).hexdigest()

            with db.get_cursor(commit=True) as cursor:
                cursor.execute("SELECT id FROM users WHERE id = %s;", (id,))
                if cursor.fetchone() is None:
                    return False, "this record does not exist"

                cursor.execute(
                    "SELECT id FROM users WHERE email_hash = %s AND id != %s;",
                    (email_hash, id),
                )
                if cursor.fetchone() is not None:
                    return False, "this email already exists"

                cursor.execute(
                    """
                    UPDATE client
                    SET name = %s, surname = %s, patronymic = %s
                    WHERE id = %s;
                    """,
                    (name, surname, patronymic if patronymic else None, id),
                )

                if password_hash:
                    cursor.execute(
                        """
                        UPDATE users
                        SET role = %s, email = %s, email_hash = %s, password_hash = %s
                        WHERE id = %s;
                        """,
                        (role, encrypted_email, email_hash, password_hash, id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users
                        SET role = %s, email = %s, email_hash = %s
                        WHERE id = %s;
                        """,
                        (role, encrypted_email, email_hash, id),
                    )

            return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"

    @staticmethod
    def delete(id):
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("SELECT id FROM users WHERE id = %s;", (id,))
                if cursor.fetchone() is None:
                    return False, "this record does not exist"

                cursor.execute("SELECT id FROM sale WHERE personal_id = %s LIMIT 1;", (id,))
                if cursor.fetchone() is not None:
                    return False, "this record has dependent sales"

                cursor.execute("SELECT id FROM delivery WHERE personal_id = %s LIMIT 1;", (id,))
                if cursor.fetchone() is not None:
                    return False, "this record has dependent deliveries"

                cursor.execute("DELETE FROM users WHERE id = %s;", (id,))
                return True, ""
        except Exception as e:
            return False, f"server error: {str(e)}"
