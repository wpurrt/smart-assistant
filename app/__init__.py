import os
from flask import Flask


from app.config import Config
from app.extensions import db, migrate, login_manager


def create_up():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_obgect(Config)

    #создаем папки
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    #расширения
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    #blueprints
    from app.main import main_bp
    from app.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app