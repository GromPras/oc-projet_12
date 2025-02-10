import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.core import bp as core_bp

    app.register_blueprint(core_bp)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    return app


from app import models
