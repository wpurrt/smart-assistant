import os
from flask import Flask
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
    from app.alice.routes import alice_bp
    from app.analytics import analytics_bp
    from app.api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(alice_bp, url_prefix="/alice")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(api_bp, url_prefix="/api")


    from flask import send_from_directory
    from flask_login import current_user, login_required
    from app.models import Task


    @app.route('/uploads/<filename>')
    @login_required
    def uploaded_file(filename):
        #проверяем что файл принадлежит пользователю
        task = Task.query.filter_by(file_path=filename, user_id=current_user.id).first()
        if not task:
            return "Нет доступа", 403
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    return app
