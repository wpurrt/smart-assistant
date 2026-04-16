from datetime import datetime

from flask import request, jsonify

from app.alice import alice_bp
from app.extensions import db
from app.models import UserAliceLink, Task
from app.services.task_service import log_user_action


def build_response(text, end_session=False):
    return {
        "response": {
            "text": text,
            "end_session": end_session
        },
        "version": "1.0"
    }


@alice_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    request_data = data.get("request", {})
    user_data = data.get("session", {}).get("user", {})
    command = (request_data.get("original_utterance") or "").lower().strip()
    yandex_user_id = user_data.get("user_id")
    if not command:
        return jsonify(build_response("Я не расслышала команду. Повторите, пожалуйста."))

    #привязываем аккаунт
    if command.startswith("привязать "):
        code = command.replace("привязать ", "").strip().upper()
        link = UserAliceLink.query.filter_by(link_code=code).first()
        if not link:
            return jsonify(build_response("Код привязки не найден."))
        link.yandex_user_id = yandex_user_id
        link.is_linked = True
        link.linked_at = datetime.utcnow()
        db.session.commit()
        return jsonify(build_response("Аккаунт успешно привязан к Алисе."))

    #для остальных комманд уже связанный аккаунт
    link = UserAliceLink.query.filter_by(yandex_user_id=yandex_user_id, is_linked=True).first()
    if not link:
        return jsonify(build_response("Сначала привяжите аккаунт. Скажите: привязать и ваш код."))
    user_id = link.user_id

    #создаем задачу
    if command.startswith("создай задачу "):
        title = command.replace("создай задачу ", "").strip()
        if not title:
            return jsonify(build_response("Не удалось определить название задачи."))
        task = Task(
            title=title,
            user_id=user_id
        )
        log_user_action(
            user_id=user_id,
            action_type="create",
            entity_type="alice_task",
            description=f"Алиса создала задачу: {task.title}"
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(build_response(f"Задача {title} успешно добавлена."))

    #показываем задачи
    if "покажи задачи" in command:
        tasks = Task.query.filter_by(user_id=user_id, is_done=False).order_by(Task.created_at.desc()).limit(5).all()
        if not tasks:
            return jsonify(build_response("У вас нет активных задач."))
        titles = ", ".join(task.title for task in tasks)
        return jsonify(build_response(f"Ваши задачи: {titles}"))

    #ближайшие задачи
    if "ближайшая задача" in command or "важная задача" in command:
        task = Task.query.filter(
            Task.user_id == user_id,
            Task.is_done.is_(False),
            Task.deadline.isnot(None)
        ).order_by(Task.deadline.asc()).first()
        if task:
            return jsonify(build_response(f"Ближайшая задача: {task.title}"))
        fallback = Task.query.filter_by(user_id=user_id, is_done=False).order_by(Task.created_at.desc()).first()
        if fallback:
            return jsonify(build_response(f"Самая свежая активная задача: {fallback.title}"))

        return jsonify(build_response("У вас нет активных задач."))
    return jsonify(build_response("Команда пока не поддерживается."))