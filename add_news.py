from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class AddFilmForm(FlaskForm):
    filmname = StringField('Название фильма', validators=[DataRequired()])
    filmadress = TextAreaField('адресс видео', validators=[DataRequired()])
    remember_new = BooleanField('Запомнить фильм')
    submit = SubmitField('Добавить')


class AddRoomForm(FlaskForm):
    roomname = StringField('Название комнаты', validators=[DataRequired()])
    roomcount = TextAreaField('Описание комнаты', validators=[DataRequired()])
    remember_new = BooleanField('Запомнить комнату')
    submit = SubmitField('Добавить')
    go = SubmitField('Перейти')


class AddCinemaForm(FlaskForm):
    cinemaname = StringField('Название кинотеатра', validators=[DataRequired()])
    remember_new = BooleanField('Запомнить кинотеатр')
    submit = SubmitField('Добавить')
    go = SubmitField('Перейти')
