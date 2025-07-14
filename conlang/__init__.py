from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

    # Выбор базы данных на основе переменной DB_TYPE
    db_type = os.getenv('DB_TYPE', 'sqlite')
    if db_type == 'sqlite':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conlang.db'
    elif db_type == 'postgresql':
        db_uri = os.getenv('DATABASE_URL')
        if not db_uri:
            raise ValueError("DATABASE_URL должен быть задан для PostgreSQL")
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    else:
        raise ValueError("DB_TYPE должен быть 'sqlite' или 'postgresql'")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Импорты моделей перед созданием таблиц
    from conlang.models import Word, Etymology
    from conlang.routes import main

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created.")

    app.register_blueprint(main)

    return app
