from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

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

    submit = SubmitField("Добавить задачу")