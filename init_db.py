import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'inventory.db'

def init_db():
    """Initialize database with required tables and sample data."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # ---------- USERS TABLE ----------
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # ---------- ITEMS TABLE ----------
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            category TEXT NOT NULL,
            price REAL DEFAULT 0
        )
    ''')

    # ---------- SAMPLE USERS ----------
    users = [
        ('admin', 'admin@.com', generate_password_hash('admin123')),
        ('user1', 'user1@.com', generate_password_hash('password1')),
        ('manager', 'manager@.com', generate_password_hash('manager123'))
    ]

    for username, email, password in users:
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        if not c.fetchone():
            c.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, password)
            )

    # ---------- SAMPLE ITEMS ----------
    items = [
        ('Laptop', 10, 'Electronics', 55000.00),
        ('Mouse', 50, 'Electronics', 499.00),
        ('Keyboard', 40, 'Electronics', 1299.00),
        ('Notebook', 100, 'Stationery', 45.00),
        ('Pen', 200, 'Stationery', 10.00),
        ('Water Bottle', 30, 'Accessories', 250.00),
        ('Headphones', 20, 'Electronics', 2200.00),
        ('Bag', 15, 'Accessories', 1200.00)
    ]

    for name, quantity, category, price in items:
        c.execute('SELECT * FROM items WHERE name = ?', (name,))
        if not c.fetchone():
            c.execute(
                'INSERT INTO items (name, quantity, category, price) VALUES (?, ?, ?, ?)',
                (name, quantity, category, price)
            )

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully with sample data!")


if __name__ == '__main__':
    init_db()

