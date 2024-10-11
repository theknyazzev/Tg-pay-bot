import sqlite3

def create_db():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        expiration_date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_subscription(user_id, expiration_date):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO subscriptions (user_id, expiration_date) VALUES (?, ?)
    ''', (user_id, expiration_date))
    conn.commit()
    conn.close()

def get_subscription_status(user_id):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT expiration_date FROM subscriptions WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None
