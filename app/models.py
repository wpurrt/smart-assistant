from datetime import datetime

from flask_login import UserMixin

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    alice_code = db.Column(db.String(12), unique=True, nullable=True)
    alice_linked = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    alice_logs = db.relationship('AliceLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    tasks = db.relationship('Task', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default='pending')  # pending / completed
    priority = db.Column(db.String(20), default='medium')  # low / medium / high

    deadline = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.title}>'


class AliceLog(db.Model):
    __tablename__ = 'alice_logs'

    id = db.Column(db.Integer, primary_key=True)

    request_text = db.Column(db.Text, nullable=True)
    response_text = db.Column(db.Text, nullable=True)
    intent = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f'<AliceLog {self.id}>'


Файл: app / services / alice_service.py
import random
import string
from app import db
from app.models import User


def generate_alice_code(length=6):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        existing = User.query.filter_by(alice_code=code).first()
        if not existing:
            return code


def ensure_alice_code(user):
    if not user.alice_code:
        user.alice_code = generate_alice_code()
        db.session.commit()
    return user.alice_code


def link_user_by_code(code):
    user = User.query.filter_by(alice_code=code).first()
    if user:
        user.alice_linked = True
        db.session.commit()
    return user


def detect_intent(command):
    command = command.lower()

    if 'создай задачу' in command or 'добавь задачу' in command:
        return 'create_task'
    if 'покажи задачи' in command or 'список задач' in command:
        return 'list_tasks'
    if 'заверши задачу' in command or 'выполни задачу' in command:
        return 'complete_task'
    if 'важная задача' in command or 'ближайшая задача' in command:
        return 'next_task'
    if 'привязать' in command or 'код' in command:
        return 'link_account'

    return 'unknown'


def create_task_from_command(user, command):
    title = command.lower()
    title = title.replace('создай задачу', '').replace('добавь задачу', '').strip()

    if not title:
        return 'Не удалось понять название задачи.'

    task = Task(
        title=title.capitalize(),
        user_id=user.id,
        status='pending',
        priority='medium'
    )
    db.session.add(task)
    db.session.commit()

    return f'Задача "{task.title}" успешно создана.'


def list_tasks_for_user(user):
    tasks = Task.query.filter_by(user_id=user.id, status='pending').order_by(Task.created_at.desc()).limit(5).all()

    if not tasks:
        return 'У вас нет активных задач.'

    task_titles = ', '.join([task.title for task in tasks])
    return f'Ваши ближайшие задачи: {task_titles}.'


def complete_task_from_command(user, command):
    title = command.lower()
    title = title.replace('заверши задачу', '').replace('выполни задачу', '').strip()

    if not title:
        return 'Назовите задачу, которую нужно завершить.'

    task = Task.query.filter(
        Task.user_id == user.id,
        Task.status == 'pending',
        Task.title.ilike(f'%{title}%')
    ).first()

    if not task:
        return 'Не удалось найти такую активную задачу.'

    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    db.session.commit()

    return f'Задача "{task.title}" отмечена как выполненная.'


def get_next_important_task(user):
    task = Task.query.filter_by(user_id=user.id, status='pending') \
        .order_by(Task.priority.desc(), Task.deadline.asc().nullslast(), Task.created_at.asc()) \
        .first()

    if not task:
        return 'У вас нет активных задач.'

    return f'Ближайшая важная задача: {task.title}.'


def save_alice_log(user, request_text, response_text, intent):
    log = AliceLog(
        user_id=user.id if user else None,
        request_text=request_text,
        response_text=response_text,
        intent=intent
    )
    db.session.add(log)
    db.session.commit()
