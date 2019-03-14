from flask import Flask, render_template, redirect, request, session
from flask_mail import Message, Mail
from loginform import LoginForm
from add_news import AddFilmForm, AddRoomForm, AddCinemaForm
from db import UserModel, FilmModel, DB, CinemaModel, RoomModel
import json

app = Flask(__name__)
mail = Mail(app)
db = DB()


@app.route('/')
@app.route('/chain/<user_id>')
def chain(user_id):
    if 'username' not in session:
        return redirect('/login')
    chain = CinemaModel(db.get_connection()).get_all(session['user_id'])
    return render_template('chain.html', username=session['username'],
                           chain=chain, user_id=user_id)


@app.route('/rooms/<int:cinema_id>')
def rooms(cinema_id):
    if 'username' not in session:
        return redirect('/login')
    rooms = RoomModel(db.get_connection()).get_cinema(cinema_id)
    return render_template('rooms.html', username=session['username'],
                           rooms=rooms, cinema_id=cinema_id, user_id=session['user_id'])


@app.route('/films/<int:room_id>/<int:cinema_id>')
def films(room_id, cinema_id):
    if 'username' not in session:
        return redirect('/add_film')
    films = FilmModel(db.get_connection()).get_room(room_id)
    return render_template('films.html', username=session['username'],
                           films=films, room_id=room_id, cinema_id=cinema_id)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/add_cinema/<int:user_id>', methods=['GET', 'POST'])
def add_cinema(user_id):
    if 'username' not in session:
        return redirect('/login')
    form = AddCinemaForm()
    if form.validate_on_submit():
        title = form.cinemaname.data
        nm = CinemaModel(db.get_connection())
        nm.insert(title, user_id)
        return redirect("/chain/{}".format(user_id))
    return render_template('add_cinema.html', title='Добавление новости',
                           form=form, username=session['username'], user_id=session['user_id'])


@app.route('/delete_cinema/<int:cinema_id>', methods=['GET'])
def delete_cinema(cinema_id):
    if 'username' not in session:
        return redirect('/login')
    nm = CinemaModel(db.get_connection())
    nm.delete(cinema_id)
    return redirect("/chain/{}".format(session['user_id']))


@app.route('/add_room/<int:cinema_id>', methods=['GET', 'POST'])
def add_room(cinema_id):
    if 'username' not in session:
        return redirect('/login')
    form = AddRoomForm()
    if form.validate_on_submit():
        title = form.roomname.data
        content = form.roomcount.data
        nm = RoomModel(db.get_connection())
        nm.insert(title, content, session['user_id'], cinema_id)
        return redirect("/rooms/{}".format(str(cinema_id)))
    return render_template('add_room.html', title='Добавление комнаты',
                           form=form, username=session['username'], cinema_id=cinema_id)


@app.route('/delete_room/<int:room_id>/<int:cinema_id>', methods=['GET'])
def delete_room(room_id, cinema_id):
    if 'username' not in session:
        return redirect('/login')
    nm = RoomModel(db.get_connection())
    nm.delete(room_id)
    return redirect("/rooms/{}".format(cinema_id))


@app.route('/add_film/<int:room_id>/<int:cinema_id>', methods=['GET', 'POST'])
def add_film(room_id, cinema_id):
    if 'username' not in session:
        return redirect('/login')
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
    names = UserModel(db.get_connection()).get_names()
    if exists[0]:
        session['username'] = user_name
        session['user_id'] = exists[1]
        session['email'] = UserModel(db.get_connection()).get(session['user_id'])[3]
        follower_notification()
        return redirect("/chain/{}".format(session['user_id']))
    else:
        if user_name in names:
            forget_password(UserModel(db.get_connection()).get_email(user_name), user_name)
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/registr', methods=['GET', 'POST'])
def registr():
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data
    email = form.email.data
    user_model = UserModel(db.get_connection())
    user_model.insert(user_name, password, email)
    if form.validate_on_submit():
        user_model.insert(user_name, password, email)
        return redirect('/login')
    return render_template('registr.html', title='Регистрация', form=form)


@app.route('/show/<path>/<int:room_id>')
def show(path, room_id):
    film = FilmModel(db.get_connection()).get_path(path)
    return '''<div>
            <iframe height="80%" width="80%" src="{}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            <a class="btn btn-primary" href="/films/{}">Вернуться в комнату</a>
            </div>'''.format(film[0], str(room_id))


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def follower_notification():
    send_email("{} is now following you!".format(session['username']),
               'nast-pota@ya.ru',
               session['email'],
               render_template("follower.txt", user=session['username']),
               render_template("follower.html", user=session['username']))


def forget_password(email, user):
    send_email("{} forget password!".format(session['username']),
               'nast-pota@ya.ru',
               email,
               render_template("forget_password.txt", user=user),
               render_template("forget_password.html", user=user))


app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
