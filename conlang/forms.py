from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class WordForm(FlaskForm):
    word = StringField('Слово', validators=[DataRequired()])
    transcription = StringField('Транскрипция')
    translation_1 = StringField('Перевод 1')
    translation_2 = StringField('Перевод 2')
    root = StringField('Корень')
    description = StringField('Описание (часть речи)')  # Новое поле
    comment = TextAreaField('Комментарий')
    submit = SubmitField('Сохранить')

class EtymologyForm(FlaskForm):
    explanation = TextAreaField('Объяснение', validators=[DataRequired()])
    comment = TextAreaField('Комментарий')
    submit = SubmitField('Сохранить')
