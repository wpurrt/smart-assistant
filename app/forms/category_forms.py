from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField(
        "Название категории",
        validators=[
            DataRequired(message="Введите название категории"),
            Length(min=2, max=100, message="Название должно быть от 2 до 100 символов")
        ]
    )

    color = StringField(
        "Цвет (HEX)",
        default="#3498db",
        validators=[
            Length(max=20)
        ]
    )

    submit = SubmitField("Добавить категорию")