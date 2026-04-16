from datetime import datetime

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.forms import TaskForm
from app.models import Task, Category
from app.tasks import tasks_bp
from app.services.task_service import log_user_action


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

    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template("tasks/list.html", form=form, tasks=tasks)


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
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    task_title = task.title

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