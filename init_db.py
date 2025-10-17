from app import get_db_connection
from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime

def init_db():
    # Establish connection to the database
    conn = get_db_connection()
    c = conn.cursor()

    # ---------------- USERS TABLE ----------------
    # Create users table if it does not exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Add the 'role' column if it is missing
    try:
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # ---------------- ITEMS TABLE ----------------
    # Create items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            category TEXT,
            price REAL DEFAULT 0
        )
    ''')

    # ---------------- BILLS TABLE ----------------
    # Create bills table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Add missing columns safely (total_amount, items)
    for column_name, column_type in [
        ("total_amount", "REAL DEFAULT 0"),
        ("items", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE bills ADD COLUMN {column_name} {column_type}")
        except sqlite3.OperationalError:
            # Column already exists
            pass

    # ---------------- BILL ITEMS TABLE ----------------
    # Create bill_items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    ''')

    # ---------------- SAMPLE USERS ----------------
    # Define some initial users
    users = [
        ('admin', 'admin@example.com', generate_password_hash('admin123'), 'admin'),
        ('user1', 'user1@example.com', generate_password_hash('password1'), 'user'),
        ('manager', 'manager@example.com', generate_password_hash('manager123'), 'user')
    ]

    # Insert sample users if they do not already exist
    for username, email, password, role in users:
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        if not c.fetchone():
            c.execute(
                'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                (username, email, password, role)
            )

    # ---------------- SAMPLE ITEMS ----------------
    # Define initial items
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

    # Insert sample items if they do not exist
    for name, quantity, category, price in items:
        c.execute('SELECT * FROM items WHERE name = ?', (name,))
        if not c.fetchone():
            c.execute(
                'INSERT INTO items (name, quantity, category, price) VALUES (?, ?, ?, ?)',
                (name, quantity, category, price)
            )

    # ---------------- SAMPLE BILL ----------------
    # Insert a sample bill if no bills exist
    c.execute('SELECT * FROM bills')
    if not c.fetchone():
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO bills (user_id, total_amount, items, date)
            VALUES (?, ?, ?, ?)
        ''', (1, 1230.00, 'Bag x1, Pen x3', date))
        bill_id = c.lastrowid

        # ---------------- SAMPLE BILL ITEMS ----------------
        bill_items = [
            (bill_id, 'Bag', 1, 1200.00),
            (bill_id, 'Pen', 3, 10.00)
        ]
        c.executemany(
            'INSERT INTO bill_items (bill_id, item_name, quantity, price) VALUES (?, ?, ?, ?)',
            bill_items
        )

    # Commit all changes and close the connection
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with all tables and sample data!")

# ---------------- RUN INITIALIZATION ----------------
if __name__ == '__main__':
    init_db()
