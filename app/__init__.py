import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["MODEL_FOLDER"], exist_ok=True)
    db.init_app(app)

    from app import models
    from app.auth import auth_bp
    from app.routes import main_bp
    from app.transactions import transactions_bp
    from app.reviews import reviews_bp
    from app.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(analytics_bp)

    with app.app_context():
        db.create_all()

    return app
