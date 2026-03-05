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
                cursor.execute("SELECT id AS id, name AS name FROM brand ORDER BY name;")
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
               b.name AS brand,
               bt.name AS body_type
            FROM model m
            JOIN brand b ON b.id = m.brand_id
            JOIN body_type bt ON bt.id = m.body_type
            ORDER by brand, model;        
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
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'temp.jpg') RETURNING id;
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

                params.append(id)

                cursor.execute(
                    f"UPDATE model SET {', '.join(updates)} WHERE id = %s;", params
                )
                return True, ""

        except Exception as e:
            return False, f"server error: {str(e)}"

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
