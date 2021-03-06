import sqlite3


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UserModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                     user_name VARCHAR(50),
                                     password_hash VARCHAR(128),
                                     email VARCHAR(50)
                                     )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash, email):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, email) 
                          VALUES (?,?,?)''', (user_name, password_hash, email))
        cursor.close()
        self.connection.commit()

    def delete(self, room_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?''', (str(room_id)))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?", (user_name, password_hash))
        except Exception as e:
            print(e)
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get_users(self, admin):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        row = cursor.fetchall()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(admin)))
        admin = cursor.fetchone()
        del row[row.index(admin)]
        return row

    def get_email(self, user):
        cursor = self.connection.cursor()
        cursor.execute("SELECT email FROM users WHERE user_name = {}".format(str(user)))
        row = cursor.fetchall()
        return row


class FilmModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS films 
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                     title VARCHAR(100),
                                     content VARCHAR(1000),
                                     user_id INT(1000),
                                     room INT(1000)
                                     )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id, room_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO films 
                          (title, content, user_id, room) 
                          VALUES (?,?,?,?)''', (title, content, str(user_id), str(room_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM films WHERE id = ?", (str(news_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM films WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM films")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM films WHERE id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()

    def get_room(self, room):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM films WHERE room = ?", (str(room)))
        row = cursor.fetchall()
        return row

    def get_path(self, film_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT content FROM films WHERE id = ?", (str(film_id)))
        row = cursor.fetchone()
        return row


class RoomModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS rooms 
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                     title VARCHAR(100),
                                     content VARCHAR(1000),
                                     user_id INT(1000),
                                     cinema INT(1000)
                                     )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id, cinema):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO rooms 
                          (title, content, user_id, cinema) 
                          VALUES (?,?,?,?)''', (title, content, str(user_id), str(cinema)))
        cursor.close()
        self.connection.commit()

    def get(self, room_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (str(room_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, cinema=None):
        cursor = self.connection.cursor()
        if cinema:
            cursor.execute("SELECT * FROM rooms WHERE cinema = ?", (str(cinema)))
        else:
            cursor.execute("SELECT * FROM rooms")
        rows = cursor.fetchall()
        return rows

    def delete(self, room_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM rooms WHERE id = ?''', (str(room_id)))
        cursor.close()
        self.connection.commit()

    def get_cinema(self, cinema):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM rooms WHERE cinema = ?", (str(cinema)))
        row = cursor.fetchall()
        return row


class CinemaModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cinemas 
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                     title VARCHAR(100),
                                     content VARCHAR(1000),
                                     user_id INT(1000)
                                     )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO cinemas 
                          (title, user_id) 
                          VALUES (?,?)''', (title, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM cinemas WHERE id = ?", (str(news_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM cinemas WHERE user_id = {}".format(str(user_id)))
        else:
            cursor.execute("SELECT * FROM cinemas")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM cinemas WHERE id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()

