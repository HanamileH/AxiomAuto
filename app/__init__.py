from flask import Flask
from flask_login import LoginManager
from flask_hcaptcha import hCaptcha
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Каптча
    app.config['HCAPTCHA_ENABLED'] = True

    hcaptcha = hCaptcha(app)

    # Авторизация
    from app.db.user import User

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Инициализация модулей
    from app.db.connection import db
    from app.routes import init_captcha

    db.init_app(app)
    db.init_db()
    init_captcha(hcaptcha)

    # Регистрация Blueprint'ов
    from app.routes import main_bp, auth_bp, admin_crud_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_crud_bp)

    return app
