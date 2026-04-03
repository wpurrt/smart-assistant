from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    username = StringField(
        "Логин",
        validators=[
            DataRequired(message="Введите логин"),
            Length(min=3, max=50, message="Логин должен быть от 3 до 50 символов")
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Введите корректный email")
        ]
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль"),
            Length(min=6, message="Пароль должен быть не менее 6 символов")
        ]
    )

    confirm_password = PasswordField(
        "Подтверждение пароля",
        validators=[
            DataRequired(message="Подтвердите пароль"),
            EqualTo("password", message="Пароли должны совпадать")
        ]
    )

    submit = SubmitField("Зарегистрироваться")

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Введите корректный email")
        ]
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль")
        ]
    )

    submit = SubmitField("Войти")