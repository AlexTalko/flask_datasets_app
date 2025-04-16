from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Загрузка конфигурации из .env
    print("Loading .env file...")
    load_dotenv()
    database_uri = os.getenv('DATABASE_URI')
    if not database_uri:
        raise ValueError("DATABASE_URI not found in .env file")
    print(f"Using DATABASE_URI: {database_uri}")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Настройка SECRET_KEY
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY',
                                         'your-secret-key-1234567890')  # Значение по умолчанию для разработки

    # Инициализация SQLAlchemy
    print("Initializing SQLAlchemy...")
    db.init_app(app)

    # Регистрация Blueprints
    print("Attempting to import and register Blueprints...")
    try:
        from app.main import main_bp
        from app.api import api_bp
        print("Blueprints imported successfully")
        app.register_blueprint(main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
        print("Blueprints registered successfully")
    except ImportError as e:
        print(f"ImportError during Blueprint registration: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during Blueprint registration: {e}")
        raise

    # Создание таблиц
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("Tables created")

    # Отладка маршрутов
    print("Registered routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")

    return app
