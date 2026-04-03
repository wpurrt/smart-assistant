from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user


from app.extensions import db
from app.models import Task
from app.tasks import tasks_bp


@tasks_bp.route("/")
@login_required
def list_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template("tasks/list.html", tasks=tasks)


@tasks_bp.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    task.is_done = not task.is_done
    db.session.commit()

    flash("Статус задачи обновлён.", "success")
    return redirect(url_for("tasks.list_tasks"))

@tasks_bp.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    db.session.delete(task)
    db.session.commit()

    flash("Задача удалена.", "info")
    return redirect(url_for("tasks.list_tasks"))
