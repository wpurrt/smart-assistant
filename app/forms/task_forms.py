from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional


class TaskForm(FlaskForm):
    title = StringField(
        "Название задачи",
        validators=[
            DataRequired(message="Введите название задачи"),
            Length(min=2, max=150, message="Название должно быть от 2 до 150 символов")
        ]
    )

    description = TextAreaField(
        "Описание (необязательно)",
        validators=[
            Length(max=1000, message="Описание не должно превышать 1000 символов")
        ]
    )

    priority = SelectField(
        "Приоритет",
        choices=[
            ("low", "Низкий"),
            ("medium", "Средний"),
            ("high", "Высокий")
        ],
        default="medium"
    )

    category_id = SelectField(
        "Категория",
        coerce=int,
        validators=[Optional()]
    )

    deadline = DateTimeLocalField(
        "Дедлайн",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()]
    )

    submit = SubmitField("Сохранить задачу")