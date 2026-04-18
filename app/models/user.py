from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
import uuid


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(225), nullable=False)

    alice_link_code = db.Column(db.String(32), unique=True)
    yandex_user_id = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_active_user = db.Column(db.Boolean, default=True)

    tasks = db.relationship(
        "Task",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    categories = db.relationship(
        "Category",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    alice_link = db.relationship(
        "UserAliceLink",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    action_logs = db.relationship(
        "ActionLog",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_alice_code(self):
        self.alice_link_code = f"ALICE-{uuid.uuid4().hex[:6].upper()}"

    def __repr__(self):
        return f"<User {self.username}>"