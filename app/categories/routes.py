from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.categories import categories_bp
from app.extensions import db
from app.forms import CategoryForm
from app.models import Category, Task
from app.services.task_service import log_user_action
import os
import uuid
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "wav"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@categories_bp.route("/", methods=["GET", "POST"])
@login_required
def list_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        existing = Category.query.filter_by(
            user_id=current_user.id,
            name=form.name.data.strip()
        ).first()
        if existing:
            flash("Такая категория уже существует.", "danger")
            return redirect(url_for("categories.list_categories"))
        category = Category(
            name=form.name.data.strip(),
            color=form.color.data.strip() or "#3498db",
            user_id=current_user.id
        )
        db.session.add(category)
        log_user_action(
            user_id=current_user.id,
            action_type="create",
            entity_type="category",
            description=f"Создана категория: {category.name}"
        )
        db.session.commit()
        flash("Категория успешно добавлена.", "success")
        return redirect(url_for("categories.list_categories"))
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.created_at.desc()).all()
    return render_template("categories/list.html", form=form, categories=categories)


@categories_bp.route("/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    category_name = category.name
    log_user_action(
        user_id=current_user.id,
        action_type="delete",
        entity_type="category",
        description=f"Удалена категория: {category_name}"
    )
    db.session.delete(category)
    db.session.commit()
    flash("Категория удалена.", "info")
    return redirect(url_for("categories.list_categories"))


@categories_bp.route("/<int:category_id>", methods=["GET", "POST"])
@login_required
def category_tasks(category_id):
    from app.forms import TaskForm
    from datetime import datetime
    form = TaskForm()

    # добавляем категории
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form.category_id.choices = [(0, "Без категории")] + [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            deadline=form.deadline.data,
            user_id=current_user.id,
            category_id=category_id
        )
        # обработка файла
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            ext = filename.rsplit(".", 1)[1].lower()
            task.file_path = filename
            task.file_type = "image" if ext in ["png", "jpg", "jpeg", "gif"] else "audio"

        db.session.add(task)
        db.session.commit()
        flash("Задача добавлена в категорию", "success")
        return redirect(url_for("categories.category_tasks", category_id=category_id))

    tasks = Task.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).all()

    return render_template(
        "tasks/list.html",
        tasks=tasks,
        form=form,
        now=datetime.utcnow()
    )