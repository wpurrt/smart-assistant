import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# from config import Config


from app.config import Config
from app.extensions import db, migrate, login_manager


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

    from app.models import User


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


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.tasks.routes import tasks_bp
    from app.categories.routes import categories_bp
    from app.profile.routes import profile_bp
    from app.analytics.routes import analytics_bp
    from app.alice.routes import alice_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(alice_bp)

    return app