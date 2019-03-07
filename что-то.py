from flask import Flask, render_template, redirect, request, session
from loginform import LoginForm
from add_news import AddNewsForm
from db import UserModel, NewsModel, DB
import json

app = Flask(__name__)
db = DB()

@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    news = NewsModel(db.get_connection()).get_all(session['user_id'])
    return render_template('news.html', username=session['username'],
                           news=news)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/news/user', methods=['GET', 'POST'])
def newsuser():
    if request.method == 'GET':
        with open("news.json", "rt", encoding="utf8") as f:
            news_list = json.loads(f.read())
        return render_template('news.html', title='Новости', news=news_list)
    elif request.method == 'POST':
        print('-')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm = NewsModel(db.get_connection())
        nm.insert(title, content, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")


@app.route('/news/admin', methods=['GET', 'POST'])
def newsadmin():
    form = AddNewsForm()
    if request.method == 'GET':
        return render_template('admin.html', title='Редактирование Новости', form=form)
    elif request.method == 'POST':
        with open("news.json", "rt", encoding="utf8") as f:
            news_list = json.loads(f.read())
        news_list['news'].append({'title': request.form['title'], 'content': request.form['content']})
        with open('news.json', 'w') as out:
            json.dump(news_list, out)
        return render_template('admin.html', title='Редактирование Новости', form=form, news=news_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data
    user_model = UserModel(db.get_connection())
    exists = user_model.exists(user_name, password)
    if exists[0]:
        session['username'] = user_name
        session['user_id'] = exists[1]
        return redirect("/index")
    else:
        user_model.insert(user_name, password)
        return render_template('login.html', title='Авторизация', form=form)
    # with open('user.json', 'w') as out:
    #     json.dump(users, out)
    # if request.form['username'] == '123' and request.form['password'] == 'qwe':
    #     return redirect('/news/admin')
    # else:
    #     return redirect('/news/user')


app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
