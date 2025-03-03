import sentry_sdk
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    sentry_sdk.init(
        dsn="https://13bd9cf5b2b9f887a5716fedb0c1c17e@o4508912268738560.ingest.de.sentry.io/4508912270442576",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )

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
