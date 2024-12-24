import sqlite3


def initiate_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def populate_db():
    products = [
        ('Vitamin C', 'Витамин C, 60 капсул, защита для иммунитета', 599),
        ('Multi-One Vitamin', 'Мултивитаминный комплекс, 30 капсул', 1200),
        ('B-Complex Vitamin', 'Б-Витамин комплекс, для энергии и антистресс', 956),
        ('Calcium, Magnesium w. V. D3', 'Способствует здоровью костей', 1299),
    ]

    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)', products)
    conn.commit()
    conn.close()


def get_all_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    conn.close()
    return products
