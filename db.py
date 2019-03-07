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
                                     password_hash VARCHAR(128)
                                     )''')
        cursor.close()
        self.connection.commit()

    # def init_table(self):
    #     cursor = self.connection.cursor()
    #     cursor.execute('''CREATE TABLE IF NOT EXISTS users
    #                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                          user_name VARCHAR(50),
    #                          password_hash VARCHAR(128)
    #                          )''')
    #     cursor.close()
    #     self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
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
        print(cursor.fetchall())
        return (True, row[0]) if row else (False,)


class NewsModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                     title VARCHAR(100),
                                     content VARCHAR(1000),
                                     user_id INTEGER
                                     )''')
        cursor.close()
        self.connection.commit()

    # def init_table(self):
    #     cursor = self.connection.cursor()
    #     cursor.execute('''CREATE TABLE IF NOT EXISTS news
    #                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                          title VARCHAR(100),
    #                          content VARCHAR(1000),
    #                          user_id INTEGER
    #                          )''')
    #     cursor.close()
    #     self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, user_id) 
                          VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id)))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT * FROM news")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()