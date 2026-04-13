import string
import random
from flask import Blueprint, render_template, abort, request, jsonify, redirect
from flask_login import login_required, current_user
from app.db import get_catalog, get_model_data, Brand, Body_type, Color, Model, ENTITIES_TYPES, STATS_TYPES, get_statistics, StaffPayment

bp = Blueprint("main", __name__)


# Главная страница (каталог)
@bp.route("/")
def main():
    all_models = get_catalog()

    return render_template("catalog.html", models=all_models)


@bp.route("/catalog/filter")
def filter_catalog():
    def parse_int(value):
        if value is None or value == "":
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def parse_float(value):
        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    filters = {
        "brand": request.args.get("brand", "").strip() or None,
        "model": request.args.get("model", "").strip() or None,
        "year_from": parse_int(request.args.get("year_from")),
        "year_to": parse_int(request.args.get("year_to")),
        "price_from": parse_int(request.args.get("price_from")),
        "price_to": parse_int(request.args.get("price_to")),
        "engine_type": request.args.get("engine_type", "").strip() or None,
        "transmission": request.args.get("transmission", "").strip() or None,
        "engine_volume_min": parse_float(request.args.get("engine_volume_min")),
        "engine_power_min": parse_int(request.args.get("engine_power_min")),
    }

    filtered_models = get_catalog(filters)

    html = render_template("_catalog_cards.html", models=filtered_models)

    return jsonify({"html": html, "count": len(filtered_models)})


# Страница описания автомобиля
@bp.route("/car/<model_id>")
def car(model_id):
    model = get_model_data(model_id)

    if model:
        return render_template("car.html", model=model)
    else:
        return abort(404)


# Страница оплаты автомобиля (mock)
@bp.route("/car/<model_id>/payment")
def car_payment(model_id):
    model = get_model_data(model_id)

    if model:
        selected_color = request.args.get("color", "")

        if not selected_color:
            return redirect(f"/car/{model_id}")
        
        color = Color.get_by_id(selected_color)[0]

        if not color:
            return abort(404)

        return render_template(
            "payment.html",
            model=model,
            selected_color=color['name'],
        )
    else:
        return abort(404)


# Страница менеджера
@bp.route("/staff/<entity_name>")
@login_required
def staff(entity_name):
    if not current_user.role in ["admin", "manager"]:
        return abort(403)

    entities = ENTITIES_TYPES
    current_entity = None

    # Скрываем вкладку users для менеджеров
    if current_user.role != "admin":
        entities = [entity for entity in entities if entity["tab_name"] != "users"]


    for entity in entities:
        if entity["tab_name"] == entity_name:
            current_entity = entity
            break
        
    # Запрещаем доступ ко вкладке users для менеджера
    if entity_name == "users" and current_user.role != "admin":
        return abort(403)


    if current_entity:
        # Генерируем случайные строки для отображения во время загрузки
        template_rows = []

        for i in range(10):
            template_rows.append(
                "".join(
                    [
                        random.choice(string.ascii_lowercase)
                        for _ in range(random.randint(5, 10))
                    ]
                )
            )

        # Данные для заполнения выпадающих списков
        brands = None
        body_types = None
        models = None
        colors = None
        payments = None

        if current_entity["tab_name"] == "models":
            brands, _ = Brand.get_all()
            body_types, _ = Body_type.get_all()

        if current_entity["tab_name"] == "cars":
            brands, _ = Brand.get_all()
            models, _ = Model.get_all()
            colors, _ = Color.get_all()

        if current_entity["tab_name"] == "payments":
            payments, error = StaffPayment.get_all()
            if error:
                return abort(500)

        return render_template(
            f"staff/{current_entity['tab_name']}.html",
            entities=entities,
            current_entity=current_entity,
            template_rows=template_rows,
            brands=brands,
            body_types=body_types,
            models=models,
            colors=colors,
            payments=payments,
        )

    else:
        return abort(404)


# Страница статистики
@bp.route("/statistics/<stats_id>")
@login_required
def statistics(stats_id):
    if not current_user.role in ["admin", "manager"]:
        return abort(403)

    entities = ENTITIES_TYPES
    
    # Скрываем вкладку users для менеджеров
    if current_user.role != "admin":
        entities = [entity for entity in entities if entity["tab_name"] != "users"]
    
    # Список всех типов статистик
    stats_types = [t["name"] for t in STATS_TYPES]

    # Данные текущей статистики
    stats_data = get_statistics(stats_id)

    if not stats_id:
        return abort(404)

    return render_template(
        "staff/statistics.html",
        stats_data=stats_data,
        stats_types=stats_types,
        entities=entities,
    )


# Информация о компании
@bp.route("/about")
def about():
    return render_template("about.html")


# Страница ошибка 401
@bp.errorhandler(401)
def unauthorized(e):
    return (
        render_template(
            "error.html",
            error_title="Ошибка 401 - Неавторизованный доступ",
            error_code="401",
            error_message="Неавторизованный доступ.",
            error_description="Вы не авторизованы. Пожалуйста, авторизуйтесь для доступа к этой странице.",
        ),
        401,
    )


# Страница ошибки 403
@bp.errorhandler(403)
def forbidden(e):
    return (
        render_template(
            "error.html",
            error_title="Ошибка 403 - Доступ запрещен",
            error_code="403",
            error_message="Доступ к странице запрещен.",
            error_description="У вас недостаточно прав для просмотра этой страницы.",
        ),
        403,
    )


# Страница ошибки 404
@bp.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "error.html",
            error_title="Ошибка 404 - Страница не найдена",
            error_code="404",
            error_message="Страница не найдена.",
            error_description="Запрашиваемая страница не существует или была удалена.",
        ),
        404,
    )


# Страница ошибки 500
@bp.errorhandler(500)
def internal_server_error(e):
    return (
        render_template(
            "error.html",
            error_title="Ошибка 500 - Внутренняя ошибка сервера",
            error_code="500",
            error_message="Внутренняя ошибка сервера.",
            error_description="Произошла ошибка на сервере. Попробуйте повторить запрос позже или обратитесь к системному администратору.",
        ),
        500,
    )
