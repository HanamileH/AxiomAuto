from flask import Flask
from flask_login import LoginManager
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Авторизация
    from app.db.user import User
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    # Инициализация модулей
    from app.db.connection import db
    db.init_app(app)
    db.init_db()

    # Регистрация Blueprint'ов
    from app.routes import main_bp, auth_bp, brand_bp, body_type_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(brand_bp)
    app.register_blueprint(body_type_bp)

    return app