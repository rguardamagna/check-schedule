from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Iniciá sesión para acceder."


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    import os
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp)

    with app.app_context():
        from app import models  # noqa

        db.create_all()

        from werkzeug.security import generate_password_hash

        if not models.User.query.first():
            db.session.add(
                models.User(
                    username="admin",
                    password_hash=generate_password_hash("admin"),
                    role="admin",
                )
            )
            db.session.add(
                models.User(
                    username="contador",
                    password_hash=generate_password_hash("contador"),
                    role="contador",
                )
            )
            db.session.commit()

    return app
