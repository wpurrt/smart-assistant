from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.forms import TaskForm
from app.models import Task, Category
from app.tasks import tasks_bp
from app.services.task_service import log_user_action
import os
from werkzeug.utils import secure_filename
from flask import current_app, request
from sqlalchemy import case
import uuid


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "wav"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@tasks_bp.route("/", methods=["GET", "POST"])
@login_required
def list_tasks():
    form = TaskForm()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    form.category_id.choices = [(0, "Без категории")] + [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            deadline=form.deadline.data,
            user_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data != 0 else None
        )
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            ext = filename.rsplit(".", 1)[1].lower()
            task.file_path = filename
            task.file_type = "image" if ext in ["png", "jpg", "jpeg", "gif"] else "audio"

        db.session.add(task)
        log_user_action(
            user_id=current_user.id,
            action_type="create",
            entity_type="task",
            description=f"Создана задача: {task.title}"
        )
        db.session.commit()

        flash("Задача успешно добавлена.", "success")
        return redirect(url_for("tasks.list_tasks"))

    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        case(
            (Task.priority == 'high', 1),
            (Task.priority == 'medium', 2),
            (Task.priority == 'low', 3),
        ),
        Task.created_at.desc()).all()

    return render_template("tasks/list.html", form=form, tasks=tasks, now=datetime.utcnow())


@tasks_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    form = TaskForm(obj=task)
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name.asc()).all()
    form.category_id.choices = [(0, "Без категории")] + [(x.id, x.name) for x in categories]

    if task.category_id:
        form.category_id.data = task.category_id
    else:
        form.category_id.data = 0

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = form.priority.data
        task.deadline = form.deadline.data
        task.category_id = form.category_id.data if form.category_id.data != 0 else None

        log_user_action(
            user_id=current_user.id,
            action_type="update",
            entity_type="task",
            description=f"Обновлена задача: {task.title}"
        )

        file = request.files.get("file")

        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            ext = filename.rsplit(".", 1)[1].lower()
            task.file_path = filename
            task.file_type = "image" if ext in ["png", "jpg", "jpeg"] else "audio"

        db.session.commit()
        flash("Задача успешно обновлена.", "success")
        return redirect(url_for("tasks.list_tasks"))

    return render_template("tasks/edit.html", form=form, task=task)


@tasks_bp.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    task.is_done = not task.is_done
    task.completed_at = datetime.utcnow() if task.is_done else None
    log_user_action(
        user_id=current_user.id,
        action_type="toggle_status",
        entity_type="task",
        description=f"Изменён статус задачи: {task.title}"
    )
    db.session.commit()

    flash("Статус задачи обновлён.", "success")
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    import os
    from flask import current_app
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task_title = task.title

    # удаляем файл
    if task.file_path:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], task.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    log_user_action(
        user_id=current_user.id,
        action_type="delete",
        entity_type="task",
        description=f"Удалена задача: {task_title}"
    )

    db.session.delete(task)
    db.session.commit()

    flash("Задача удалена.", "info")
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/upload/<int:task_id>", methods=["POST"])
@login_required
def upload_file(task_id):
    task = Task.query.get_or_404(task_id)
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Файл не выбран", "danger")
        return redirect(url_for("tasks.list_tasks"))

    if not allowed_file(file.filename):
        flash("Недопустимый формат", "danger")
        return redirect(url_for("tasks.list_tasks"))

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    ext = filename.rsplit(".", 1)[1].lower()
    file_type = "image" if ext in ["png", "jpg", "jpeg", "gif"] else "audio"
    task.file_path = filename
    task.file_type = file_type

    db.session.commit()
    flash("Файл загружен", "success")
    return redirect(url_for("tasks.list_tasks"))