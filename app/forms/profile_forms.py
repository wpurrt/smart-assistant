from flask_wtf import FlaskForm
from wtforms import SubmitField


class GenerateAliceCodeForm(FlaskForm):
    submit = SubmitField("Сгенерировать код привязки")