from app.models import User, Task, Category
from app import db
from datetime import datetime
import requests


def handle_alice_command(data):
    request = data.get("request", {})
    command = request.get("command", "")
    command = command.lower()
    yandex_id = (
        data.get("session", {})
        .get("user", {})
        .get("user_id", "")
    )

    #привязка
    if any(x in command for x in ["привязать аккаунт", "привяжи аккаунт"]):
        code = command.split()[-1].upper()
        user = User.query.filter_by(alice_link_code=code).first()
        if not user:
            return simple_response("Неверный код")
        user.yandex_user_id = yandex_id
        user.alice_link_code = None
        db.session.commit()
        return simple_response("Аккаунт привязан")
    user = User.query.filter_by(yandex_user_id=yandex_id).first()
    if not user:
        return simple_response("Сначала привяжите аккаунт")

    #создание задачи
    if any(x in command for x in ["создай задачу", "добавь задачу", "новая задача"]):
        text = command.replace("создай задачу", "").strip()
        category = None
        for c in user.categories:
            if c.name.lower() in text:
                category = c
        task = Task(
            title=text or "Новая задача",
            user_id=user.id,
            category_id=category.id if category else None
        )
        db.session.add(task)
        db.session.commit()
        return simple_response(f"Создала задачу: {task.title}")

    #покажи задачи
    if any(x in command for x in ["покажи задачи", "мои задачи", "список задач"]):
        tasks = Task.query.filter_by(user_id=user.id, is_done=False).all()
        if not tasks:
            return simple_response("У вас нет задач")
        text = []
        for t in tasks:
            line = t.title
            if t.deadline:
                line += f" до {t.deadline.strftime('%d.%m')}"
            if t.file_path:
                line += " (есть файл)"
            text.append(line)
        return simple_response("Ваши задачи: " + ", ".join(text))

    #завершаем задачу
    if any(x in command for x in ["заверши задачу", "закрой задачу", "выполнил задачу", "выполнила задачу"]):
        title = command.replace("заверши задачу", "").strip()
        task = Task.query.filter_by(user_id=user.id, title=title).first()
        if not task:
            return simple_response("Не нашла задачу")
        task.is_done = True
        task.completed_at = datetime.utcnow()
        db.session.commit()
        return simple_response("Готово")

    #дедлайн
    if "дедлайн" in command:
        return simple_response("Пока установите дедлайн через сайт")

    #погода
    if "погода" in command:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 52.37,
                "longitude": 4.90,
                "current_weather": True
            }
        )
        data = r.json()
        temp = data["current_weather"]["temperature"]
        return simple_response(f"Сейчас {temp} градусов")


def simple_response(text):
    return {
        "response": {
            "text": text,
            "tts": text,
            "end_session": False,
            "buttons": [
                {
                    "title": "Открыть сайт",
                    "url": "https://smart-assistant--wppurt.replit.app"
                }
            ]
        },
        "version": "1.0"
    }
