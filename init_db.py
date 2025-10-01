import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('inventory.db')
c = conn.cursor()

# Create Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')
# Create Items table
c.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
)
''')

conn.commit()
conn.close()

print("Database initialized successfully!")
