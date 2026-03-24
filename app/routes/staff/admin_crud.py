import os
import uuid
from flask import Blueprint, request, jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.db import Brand, Body_type, Color, Model, Car, StaffUser, manager_required

OBJECTS_MATCH = {
    "brands": Brand,
    "body_types": Body_type,
    "colors": Color,
    "models": Model,
    "cars": Car,
    "users": StaffUser,
}

bp = Blueprint("staff/admin_crud", __name__)
MODEL_IMAGE_DIR = "/app/static/img/cars"
MODEL_IMAGE_PREFIX = "cars"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def check_users_admin_access(object_name):
    if object_name == "users" and current_user.role != "admin":
        return jsonify({"success": False, "error": "forbidden"}), 403

    return None


def remove_model_image(image_path):
    if not image_path:
        return

    normalized_path = image_path.replace("\\", "/").lstrip("/")
    if not normalized_path.startswith(f"{MODEL_IMAGE_PREFIX}/"):
        return

    absolute_path = os.path.join(MODEL_IMAGE_DIR, os.path.basename(normalized_path))

    if os.path.exists(absolute_path):
        os.remove(absolute_path)


def save_model_image(image_file):
    if image_file is None or not image_file.filename:
        return None, "Image is required"

    filename = secure_filename(image_file.filename)

    if "." not in filename:
        return None, "Invalid file name"

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Unsupported image format"

    os.makedirs(MODEL_IMAGE_DIR, exist_ok=True)
    final_filename = f"{uuid.uuid4().hex}.{extension}"
    final_path = os.path.join(MODEL_IMAGE_DIR, final_filename)
    image_file.save(final_path)
    return f"{MODEL_IMAGE_PREFIX}/{final_filename}", ""


def parse_model_request_data():
    payload = request.form if request.content_type and "multipart/form-data" in request.content_type else request.get_json(silent=True)
    payload = payload or {}

    name = payload.get("name")
    description = payload.get("description")
    engine_type = payload.get("engine_type")
    transmission = payload.get("transmission")
    brand_id = payload.get("brand_id")
    body_type_id = payload.get("body_type_id")

    try:
        price = int(payload.get("price"))
        year = int(payload.get("year"))
        engine_power = int(payload.get("engine_power"))
        engine_volume_raw = payload.get("engine_volume")
        engine_volume = (
            None
            if engine_type == "electric" or engine_volume_raw in (None, "")
            else float(engine_volume_raw)
        )
        brand_id = int(brand_id) if brand_id is not None else None
        body_type_id = int(body_type_id) if body_type_id is not None else None
    except (TypeError, ValueError):
        return None, "Invalid numeric fields"

    data = {
        "name": name,
        "description": description,
        "price": price,
        "year": year,
        "engine_type": engine_type,
        "engine_power": engine_power,
        "engine_volume": engine_volume,
        "transmission": transmission,
        "brand_id": brand_id,
        "body_type_id": body_type_id,
    }
    return data, ""

# GET-запрос на получение всех записей объекта
@bp.route("/api/crud/<object_name>", methods=["GET"])
@manager_required
def get_all(object_name):
    try:
        object_name = object_name.strip().lower()

        forbidden_response = check_users_admin_access(object_name)
        if forbidden_response:
            return forbidden_response

        # Получаем класс нужного объекта
        object_class = OBJECTS_MATCH.get(object_name)

        if object_class is None:
            return (
                jsonify({"success": False, "error": f"Object {object_name} not found"}),
                404,
            )

        # Получаем все объекты класса
        rows, error = object_class.get_all()

        if error:
            return jsonify({"success": False, "error": error}), 500

        # Возвращаем объекты
        return jsonify({"success": True, "data": rows})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# POST-запрос на создание нового объекта
@bp.route("/api/crud/<object_name>", methods=["POST"])
@manager_required
def create(object_name):
    try:
        object_name = object_name.strip().lower()

        forbidden_response = check_users_admin_access(object_name)
        if forbidden_response:
            return forbidden_response

        # Получаем класс нужного объекта
        object_class = OBJECTS_MATCH.get(object_name)

        if object_class is None:
            return (
                jsonify({"success": False, "error": f"Object {object_name} not found"}),
                404,
            )

        # Получаем данные из запроса
        data = request.get_json(silent=True) or {}

        # ----- Добавляем запись -----
        # Производители
        if object_name == "brands":
            name = data.get("name")

            if not name:
                return jsonify({"success": False, "error": "Name is required"}), 400

            id, error = Brand.create(name=name)

        # Типы кузовов
        elif object_name == "body_types":
            name = data.get("name")

            if not name:
                return jsonify({"success": False, "error": "Name is required"}), 400

            id, error = Body_type.create(name=name)

        # Цвета
        elif object_name == "colors":
            name = data.get("name")
            hex_code = data.get("hex_code")

            if not name:
                return jsonify({"success": False, "error": "Name is required"}), 400

            if not hex_code:
                return jsonify({"success": False, "error": "Hex code is required"}), 400

            id, error = Color.create(name=name, hex_code=hex_code)

        # Модели
        elif object_name == "models":
            model_data, parse_error = parse_model_request_data()
            if parse_error:
                return jsonify({"success": False, "error": parse_error}), 400

            image_path, image_error = save_model_image(request.files.get("image"))
            if image_error:
                return jsonify({"success": False, "error": image_error}), 400

            name = model_data["name"]
            description = model_data["description"]
            price = model_data["price"]
            year = model_data["year"]
            engine_type = model_data["engine_type"]
            engine_power = model_data["engine_power"]
            engine_volume = model_data["engine_volume"]
            transmission = model_data["transmission"]
            brand_id = model_data["brand_id"]
            body_type_id = model_data["body_type_id"]

            if not name:
                return jsonify({"success": False, "error": "Name is required"}), 400

            if not description:
                return (
                    jsonify({"success": False, "error": "Description is required"}),
                    400,
                )

            if not price:
                return jsonify({"success": False, "error": "Price is required"}), 400

            if not year:
                return jsonify({"success": False, "error": "Year is required"}), 400

            if not engine_type:
                return (
                    jsonify({"success": False, "error": "Engine type is required"}),
                    400,
                )

            if not engine_power:
                return (
                    jsonify({"success": False, "error": "Engine power is required"}),
                    400,
                )

            if engine_type != "electric" and not engine_volume:
                return (
                    jsonify({"success": False, "error": "Engine volume is required"}),
                    400,
                )

            if not transmission:
                return (
                    jsonify({"success": False, "error": "Transmission is required"}),
                    400,
                )

            if not brand_id:
                return jsonify({"success": False, "error": "Brand is required"}), 400

            if not body_type_id:
                return (
                    jsonify({"success": False, "error": "Body type is required"}),
                    400,
                )

            id, error = Model.create(
                name=name,
                description=description,
                price=price,
                year=year,
                engine_type=engine_type,
                engine_power=engine_power,
                engine_volume=engine_volume,
                transmission=transmission,
                brand_id=brand_id,
                body_type_id=body_type_id,
                image_path=image_path,
            )

            if error:
                remove_model_image(image_path)

        # Автомобили
        elif object_name == "cars":
            vin = data.get("vin")
            model_id = data.get("model_id")
            color_id = data.get("color_id")

            if not vin:
                return jsonify({"success": False, "error": "VIN is required"}), 400

            if len(vin.strip()) != 17:
                return (
                    jsonify({"success": False, "error": "VIN must be 17 characters"}),
                    400,
                )

            if not model_id:
                return jsonify({"success": False, "error": "Model is required"}), 400

            if not color_id:
                return jsonify({"success": False, "error": "Color is required"}), 400

            id, error = Car.create(
                model_id=int(model_id),
                color_id=int(color_id),
                vin=vin.strip().upper(),
            )

        # Пользователи
        elif object_name == "users":
            name = data.get("name")
            surname = data.get("surname")
            patronymic = data.get("patronymic")
            email = data.get("email")
            password = data.get("password")
            role = data.get("role")

            if not all([name, surname, email, password, role]):
                return (
                    jsonify({"success": False, "error": "required fields are missing"}),
                    400,
                )

            id, error = StaffUser.create(
                name=name,
                surname=surname,
                patronymic=patronymic,
                email=email,
                password=password,
                role=role,
            )

        # Неизвестный объект
        else:
            return (
                jsonify({"success": False, "error": f"Object {object_name} not found"}),
                404,
            )
        # -----------------------------

        # Обработка ошибок
        if error:
            return jsonify({"success": False, "error": error}), 500

        # Возвращаем результат
        return jsonify({"success": True, "id": id}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# PUT-запрос на изменение объекта
@bp.route("/api/crud/<object_name>/<int:id>", methods=["PUT"])
@manager_required
def update(object_name, id):
    try:
        object_name = object_name.strip().lower()

        forbidden_response = check_users_admin_access(object_name)
        if forbidden_response:
            return forbidden_response

        # Получаем класс нужного объекта
        object_class = OBJECTS_MATCH.get(object_name)

        if object_class is None:
            return (
                jsonify({"success": False, "error": f"Object {object_name} not found"}),
                404,
            )

        # Получаем данные из запроса
        data = request.get_json(silent=True) if request.is_json else request.form
        data = data or {}

        # ----- Обновляем запись -----
        # Производители
        if object_name == "brands":
            name = data.get("name")

            if not name:
                return jsonify({"success": False, "error": "Name is required"}), 400

            _, error = Brand.update(id=id, name=name)

        # Типы кузовов
        elif object_name == "body_types":
            name = data.get("name")

            if not name:
                return jsonify({"success": False, "error": "Name is required"}), 400

            _, error = Body_type.update(id=id, name=name)

        # Цвета
        elif object_name == "colors":
            name = data.get("name")
            hex_code = data.get("hex_code")

            if not name or not hex_code:
                return (
                    jsonify(
                        {"success": False, "error": "Name or hex code are required"}
                    ),
                    400,
                )

            _, error = Color.update(id=id, name=name, hex_code=hex_code)

        # Модели
        elif object_name == "models":
            model_data, parse_error = parse_model_request_data()
            if parse_error:
                return jsonify({"success": False, "error": parse_error}), 400

            old_image_path, old_image_error = Model.get_image_path(id=id)
            if old_image_error:
                return jsonify({"success": False, "error": old_image_error}), 404

            new_image_path = None
            image_file = request.files.get("image")
            if image_file and image_file.filename:
                new_image_path, image_error = save_model_image(image_file)
                if image_error:
                    return jsonify({"success": False, "error": image_error}), 400

            name = model_data["name"]
            description = model_data["description"]
            price = model_data["price"]
            year = model_data["year"]
            engine_type = model_data["engine_type"]
            engine_power = model_data["engine_power"]
            engine_volume = model_data["engine_volume"]
            transmission = model_data["transmission"]
            brand_id = model_data["brand_id"]
            body_type_id = model_data["body_type_id"]

            _, error = Model.update(
                id=id,
                name=name,
                description=description,
                price=price,
                year=year,
                engine_type=engine_type,
                engine_power=engine_power,
                engine_volume=engine_volume,
                transmission=transmission,
                brand_id=brand_id,
                body_type_id=body_type_id,
                image_path=new_image_path,
            )

            if error and new_image_path:
                remove_model_image(new_image_path)

            if not error and new_image_path:
                remove_model_image(old_image_path)

        # Автомобили
        elif object_name == "cars":
            vin = data.get("vin")
            model_id = data.get("model_id")
            color_id = data.get("color_id")

            if not vin:
                return jsonify({"success": False, "error": "VIN is required"}), 400

            if len(vin.strip()) != 17:
                return (
                    jsonify({"success": False, "error": "VIN must be 17 characters"}),
                    400,
                )

            if not model_id:
                return jsonify({"success": False, "error": "Model is required"}), 400

            if not color_id:
                return jsonify({"success": False, "error": "Color is required"}), 400

            _, error = Car.update(
                id=id,
                model_id=int(model_id),
                color_id=int(color_id),
                vin=vin.strip().upper(),
            )

        # Пользователи
        elif object_name == "users":
            name = data.get("name")
            surname = data.get("surname")
            patronymic = data.get("patronymic")
            email = data.get("email")
            role = data.get("role")
            new_password = data.get("new_password")

            if not all([name, surname, email, role]):
                return (
                    jsonify({"success": False, "error": "required fields are missing"}),
                    400,
                )

            _, error = StaffUser.update(
                id=id,
                name=name,
                surname=surname,
                patronymic=patronymic,
                email=email,
                role=role,
                new_password=new_password,
            )

        # Неизвестный объект
        else:
            return (
                jsonify({"success": False, "error": f"Object {object_name} not found"}),
                404,
            )
        # -----------------------------

        # Обработка ошибок
        if error:
            return jsonify({"success": False, "error": error}), 500

        # Возвращаем результат
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# DELETE-запрос на удаление объекта
@bp.route("/api/crud/<object_name>/<int:id>", methods=["DELETE"])
@manager_required
def delete(object_name, id):
    try:
        object_name = object_name.strip().lower()

        forbidden_response = check_users_admin_access(object_name)
        if forbidden_response:
            return forbidden_response

        # Получаем класс нужного объекта
        object_class = OBJECTS_MATCH.get(object_name)

        if object_class is None:
            return (
                jsonify({"success": False, "error": f"Object {object_name} not found"}),
                404,
            )

        if object_name == "models":
            image_path, image_error = Model.get_image_path(id=id)
            if image_error:
                return jsonify({"success": False, "error": image_error}), 404
        else:
            image_path = None

        # Удаляем запись
        success, error = object_class.delete(id=id)

        # Обработка ошибок
        if error:
            return jsonify({"success": False, "error": error}), 500

        if object_name == "models":
            remove_model_image(image_path)

        # Возвращаем результат
        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
