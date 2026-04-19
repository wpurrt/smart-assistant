import os
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager
from app.alice.routes import alice_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    #создаем папки
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    #расширения
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User, Task, Category, ActionLog, UserAliceLink


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #blueprints
    from app.main import main_bp
    from app.auth import auth_bp
    from app.tasks import tasks_bp
    from app.categories import categories_bp
    from app.profile import profile_bp
    from app.alice import alice_bp
    from app.analytics import analytics_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(alice_bp, url_prefix="/alice")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")

    return app