from app import get_db_connection
from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # ---------- USERS TABLE ----------
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # Add missing 'role' column
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except sqlite3.OperationalError:
        pass  # Already exists

    # ---------- ITEMS TABLE ----------
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    category TEXT,
                    price REAL DEFAULT 0
                )''')

    # ---------- BILLS TABLE ----------
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )''')

    # Add missing columns safely
    for col_def in [
        ("total_amount", "REAL DEFAULT 0"),
        ("items", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE bills ADD COLUMN {col_def[0]} {col_def[1]}")
        except sqlite3.OperationalError:
            pass

    # ---------- BILL ITEMS TABLE ----------
    c.execute('''CREATE TABLE IF NOT EXISTS bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER,
                    item_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    FOREIGN KEY (bill_id) REFERENCES bills(id)
                )''')

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
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO bills (user_id, total_amount, items, date)
            VALUES (?, ?, ?, ?)
        ''', (1, 1230.00, 'Bag x1, Pen x3', date))
        bill_id = c.lastrowid

        # ---------- SAMPLE BILL ITEMS ----------
        bill_items = [
            (bill_id, 'Bag', 1, 1200.00),
            (bill_id, 'Pen', 3, 10.00)
        ]
        c.executemany(
            'INSERT INTO bill_items (bill_id, item_name, quantity, price) VALUES (?, ?, ?, ?)',
            bill_items
        )

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with sample data (users, items, bills, bill_items)!")

if __name__ == '__main__':
    init_db()
