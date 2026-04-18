from app.models import User, Task
from app import db
from datetime import datetime


def handle_alice_command(data):
    command = data["request"]["command"].lower()
    yandex_id = data["session"]["user"]["user_id"]

    #привязка аккаунта
    if "привязать аккаунт" in command:
        code = command.split()[-1].upper()
        user = User.query.filter_by(alice_link_code=code).first()
        if not user:
            return "Неверный код привязки"
        user.yandex_user_id = yandex_id
        user.alice_link_code = None
        db.session.commit()
        return "Аккаунт успешно привязан"

    #поиск пользователя
    user = User.query.filter_by(yandex_user_id=yandex_id).first()
    if not user:
        return "Аккаунт не привязан"

    #показ задач
    if "покажи задачи" in command:
        tasks = Task.query.filter_by(user_id=user.id, is_done=False).all()
        if not tasks:
            return "У вас нет задач"
        return "Ваши задачи: " + ", ".join([t.title for t in tasks])

    #создание задачи
    if "создай задачу" in command:
        title = command.replace("создай задачу", "").strip()
        task = Task(
            title=title,
            user_id=user.id
        )
        db.session.add(task)
        db.session.commit()
        return f"Задача {title} создана"

    #завершение задачи
    if "заверши задачу" in command:
        title = command.replace("заверши задачу", "").strip()
        task = Task.query.filter_by(user_id=user.id, title=title).first()
        if not task:
            return "Задача не найдена"
        task.is_done = True
        task.completed_at = datetime.utcnow()
        db.session.commit()
        return f"Задача {title} завершена"

    #ближайшая задача
    if "ближайшая задача" in command:
        task = Task.query.filter_by(user_id=user.id, is_done=False).order_by(Task.due_date).first()
        if not task:
            return "Нет задач"
        return f"Ближайшая задача: {task.title}"

    return "Я не поняла команду"