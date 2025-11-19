from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация модулей
    #from app import database
    #database.init_db()

    from app.db.connection import db
    db.init_app(app)

    # Регистрация Blueprint'ов
    from app.routes import main_bp, auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app