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
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
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

    # ---------- BILLS TABLE ----------
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            items TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---------- SAMPLE USERS ----------
    users = [
        ('admin', 'admin@example.com', generate_password_hash('admin123'), 'admin'),
        ('user1', 'user1@example.com', generate_password_hash('password1'), 'user'),
        ('manager', 'manager@example.com', generate_password_hash('manager123'), 'user')
    ]

    for username, email, password, role in users:
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        if not c.fetchone():
            c.execute(
                'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                (username, email, password, role)
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

    # ---------- SAMPLE BILL ----------
    c.execute('SELECT * FROM bills')
    if not c.fetchone():
        c.execute('''
            INSERT INTO bills (user_id, total_amount, items)
            VALUES (?, ?, ?)
        ''', (1, 1200.00, 'Bag x1, Pen x3'))

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully with sample data (users, items, bills)!")

if __name__ == '__main__':
    init_db()
