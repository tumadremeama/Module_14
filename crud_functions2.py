import sqlite3


def initiate_db():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                balance INTEGER NOT NULL DEFAULT 1000
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f'Ошибка при работе с базой данных: {e}')
    finally:
        conn.close()


def add_user(username, email, age):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)''',
                       (username, email, age, 1000))
        conn.commit()
    except sqlite3.Error as e:
        print(f'Ошибка при добавлении пользователя: {e}')
    finally:
        conn.close()


def is_included(username):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    except sqlite3.Error as e:
        print(f'Ошибка при проверке пользователя: {e}')
        return False
    finally:
        conn.close()