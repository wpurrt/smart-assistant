from flask import Blueprint, jsonify, request, current_app
from app.models import Task
from app.extensions import db
from flask_login import login_required, current_user
from flask import abort
import os
import uuid
from werkzeug.utils import secure_filename


api_bp = Blueprint("api", __name__)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "wav"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route("/tasks/<int:task_id>/upload", methods=["POST"])
@login_required
def upload_file_api(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    file = request.files.get("file")
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    task.file_path = filename
    task.file_type = "image"
    db.session.commit()
    return jsonify({"message": "File uploaded"})


@api_bp.route("/tasks", methods=["GET"])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {"id": t.id, "title": t.title, "done": t.is_done}
        for t in tasks
    ])


@api_bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.json
    task = Task(
        title=data["title"],
        user_id=current_user.id
    )
    if "title" not in data:
        return jsonify({"error": "Title required"}), 400
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created"})


@api_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.json
    task.title = data.get("title", task.title)
    task.is_done = data.get("done", task.is_done)
    db.session.commit()
    return jsonify({"message": "Task updated"})


@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task_api(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})