from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    from app.config import Config
    app.config.from_object(Config)

    db.init_app(app)

    # Keep your existing blueprint registrations here.
    # Keep your existing database initialization logic here.

    return app