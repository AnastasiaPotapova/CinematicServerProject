from flask import Flask, render_template, redirect, request, session
from flask_mail import Message, Mail
from loginform import LoginForm
from add_news import AddFilmForm, AddRoomForm, AddCinemaForm
from db import UserModel, FilmModel, DB, CinemaModel, RoomModel
from Errors import LengthError, LetterError, DigitError, SequenceError
import json

app = Flask(__name__)

app.config.update(dict(
    DEBUG=False,
    MAIL_SERVER='smtp.yandex.ru',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='nast-pota@ya.ru',
    MAIL_PASSWORD='gjnfgjdf10',
))

mail = Mail(app)
db = DB()
admins = ['main_admin']


def check_password(password):
    try:
        if len(password) <= 8:
            raise LengthError

        if password == password.lower() or password == password.upper():
            raise LetterError

        x = [d in '1234567890' for d in list(password)]

        if not (True in x and False in x):
            raise DigitError

        for i in range(len(password) - 2):
            if password[i:i + 3].lower() in 'qwertyuiop':
                raise SequenceError
            elif password[i:i + 3].lower() in 'asdfghjkl':
                raise SequenceError
            elif password[i:i + 3].lower() in 'zxcvbnm':
                raise SequenceError
            elif password[i:i + 3].lower() in 'йцукенгшщзхъ':
                raise SequenceError
            elif password[i:i + 3].lower() in 'фывапролджэё':
                raise SequenceError
            elif password[i:i + 3].lower() in 'ячсмитьбю':
                raise SequenceError

        return (True,)

    except LengthError:
        return (False, 'Пароль короткий!')
    except LetterError:
        return (False, 'В пароле использованы только строчные или только заглавные буквы.')
    except DigitError:
        return (False, 'Пароль состоит только из цифр или не имеет их вовсе.')
    except SequenceError:
        return (False, 'Пароль имеет сочетание трех подрядидущих букв на клавиатуре.')


@app.route('/')
@app.route('/chain/<user_id>')
def chain(user_id):
    chain = CinemaModel(db.get_connection()).get_all(user_id)
    return render_template('chain.html', username=session['username'],
                           chain=chain, user_id=user_id)


@app.route('/users')
def users():
    users = UserModel(db.get_connection()).get_users(session['user_id'])
    return render_template('users.html', username=session['username'],
                           users=users)


@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    nm = UserModel(db.get_connection())
    nm.delete(user_id)
    return redirect("/users")


@app.route('/rooms/<int:cinema_id>/<int:user_id>')
def rooms(cinema_id, user_id):
    rooms = RoomModel(db.get_connection()).get_cinema(cinema_id)
    return render_template('rooms.html', username=session['username'],
                           rooms=rooms, cinema_id=cinema_id, user_id=user_id)


@app.route('/films/<int:room_id>/<int:cinema_id>/<int:user_id>')
def films(room_id, cinema_id, user_id):
    films = FilmModel(db.get_connection()).get_room(room_id)
    return render_template('films.html', username=session['username'],
                           films=films, room_id=room_id, cinema_id=cinema_id, user_id=user_id)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/add_cinema/<int:user_id>', methods=['GET', 'POST'])
def add_cinema(user_id):
    form = AddCinemaForm()
    if form.validate_on_submit():
        title = form.cinemaname.data
        nm = CinemaModel(db.get_connection())
        nm.insert(title, user_id)
        return redirect("/chain/{}".format(user_id))
    return render_template('add_cinema.html', title='Добавление кинотеатра',
                           form=form, username=session['username'], user_id=user_id)


@app.route('/delete_cinema/<int:cinema_id>', methods=['GET'])
def delete_cinema(cinema_id):
    nm = CinemaModel(db.get_connection())
    rooms = [x[0] for x in RoomModel(db.get_connection()).get_all(cinema_id)]
    nm.delete(cinema_id)
    rooms = [delete_room(x, cinema_id) for x in rooms]
    return redirect("/chain/{}".format(session['user_id']))


@app.route('/add_room/<int:cinema_id>', methods=['GET', 'POST'])
def add_room(cinema_id):
    form = AddRoomForm()
    if form.validate_on_submit():
        title = form.roomname.data
        content = form.roomcount.data
        nm = RoomModel(db.get_connection())
        nm.insert(title, content, session['user_id'], cinema_id)
        return redirect("/rooms/{}".format(str(cinema_id)))
    return render_template('add_room.html', title='Добавление комнаты',
                           form=form, username=session['username'], cinema_id=cinema_id)


@app.route('/delete_room/<int:room_id>/<int:cinema_id>/<int:user_id>', methods=['GET'])
def delete_room(room_id, cinema_id, user_id):
    nm = RoomModel(db.get_connection())
    films = [x[0] for x in FilmModel(db.get_connection()).get_all(room_id)]
    nm.delete(room_id)
    films = [delete_film(x, room_id) for x in films]
    return redirect("/rooms/{}/{}".format(cinema_id, user_id))


@app.route('/add_film/<int:room_id>/<int:cinema_id>', methods=['GET', 'POST'])
def add_film(room_id, cinema_id):
    form = AddFilmForm()
    if form.validate_on_submit():
        name = form.filmname.data
        content = form.filmadress.data
        nm = FilmModel(db.get_connection())
        nm.insert(name, content, session['user_id'], room_id)
        return redirect("/films/{}/{}".format(str(room_id), str(cinema_id)))
    return render_template('add_film.html', title='Добавление фильма',
                           form=form, username=session['username'], room_id=room_id)


@app.route('/delete_film/<int:film_id>/<int:room_id>', methods=['GET'])
def delete_film(film_id, room_id):
    if 'username' not in session:
        return redirect('/login')
    nm = FilmModel(db.get_connection())
    nm.delete(film_id)
    return redirect("/films/{}".format(room_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data
    user_model = UserModel(db.get_connection())
    exists = user_model.exists(user_name, password)
    names = [x for x in UserModel(db.get_connection()).get_all()]
    print(names)
    if exists[0]:
        session['username'] = user_name
        session['user_id'] = exists[1]
        session['email'] = UserModel(db.get_connection()).get(session['user_id'])[3]
        print('-')
        if user_name in admins:
            return redirect("/users")
        else:
            return redirect("/chain/{}".format(session['user_id']))
    else:
        if user_name in names:
            print('-')
            forget_password(UserModel(db.get_connection()).get_email(user_name), user_name)
        else:
            return render_template('login.html', title='Авторизация', form=form, error='Вас нет в базе')
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/registr', methods=['GET', 'POST'])
def registr():
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data
    email = form.email.data
    user_model = UserModel(db.get_connection())
    names = [x for x in UserModel(db.get_connection()).get_all()]
    if form.validate_on_submit():
        if user_name in names:
            return render_template('registr.html', title='Регистрация', form=form, usernameerror='никнейм занят')
        else:
            a = check_password(password)
            if a[0]:
                user_model.insert(user_name, password, email)
                follower_notification(user_name, email)
                return redirect('/login')
            else:
                return render_template('registr.html', title='Регистрация', form=form, passworderror=a[1])
    return render_template('registr.html', title='Регистрация', form=form)


@app.route('/show/<int:film_id>/<int:room_id>/<int:cinema_id>/<int:user_id>')
def show(film_id, room_id, cinema_id, user_id):
    film = FilmModel(db.get_connection()).get(film_id)
    return '''<div>
            {}
            <a class="btn btn-primary" href="/films/{}/{}/{}">Вернуться в комнату</a>
            </div>'''.format(film[2], str(room_id), str(cinema_id), str(user_id))


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def follower_notification(username, email):
    send_email("{} зарегистрировался в систему кинотеатров!".format(username),
               'nast-pota@ya.ru',
               [email],
               render_template("follower.txt", user=username),
               render_template("follower.html", user=username))


def forget_password(email, user):
    send_email("{} forget password!".format(user),
               'nast-pota@ya.ru',
               [email],
               render_template("forget_password.txt", username=user),
               render_template("forget_password.html", username=user))


app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
