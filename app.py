from flask import Flask, render_template, request, redirect, session, jsonify, url_for , flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'inventory.db'

# =================== Helper ===================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# =================== Routes ===================

# About Page (initial page)
@app.route('/')
def about():
    return render_template('about.html')

# Home Page
@app.route('/home')
def home():
    return render_template('index.html')

# =================== Register ===================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
        if c.fetchone():
            conn.close()
            flash("Username or email already exists!", "error")
            return redirect(url_for('register'))

        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hashed_password))
        conn.commit()
        conn.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# =================== Login ===================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']

        # Connect to DB
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()

        # Check if username or email exists
        c.execute("SELECT * FROM users WHERE username=? OR email=?", 
                  (username_or_email, username_or_email))
        user = c.fetchone()
        conn.close()

        # Validate user
        if user and check_password_hash(user[3], password):  # password is at index 3
            session['user'] = user[0]
            return redirect('/dashboard')
        else:
            flash("Invalid username or password!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# =================== Logout ===================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# =================== Dashboard ===================
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM items")
    categories = [row['category'] for row in c.fetchall() if row['category']]
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.close()
    return render_template('dashboard.html', items=items, categories=categories)

# =================== AJAX Search / Filter / Sort ===================
@app.route('/search_items', methods=['POST'])
def search_items():
    if 'user' not in session:
        return jsonify([])

    data = request.get_json()
    search_query = data.get('search', '').strip()
    category_filter = data.get('category', '').strip()
    sort_option = data.get('sort', '').strip()

    conn = get_db_connection()
    c = conn.cursor()
    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if category_filter and category_filter != "All":
        query += " AND category=?"
        params.append(category_filter)

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    if sort_option == "price_asc":
        query += " ORDER BY price ASC"
    elif sort_option == "price_desc":
        query += " ORDER BY price DESC"
    elif sort_option == "quantity_asc":
        query += " ORDER BY quantity ASC"
    elif sort_option == "quantity_desc":
        query += " ORDER BY quantity DESC"

    c.execute(query, tuple(params))
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(results)

# =================== Add Item ===================
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO items (name, category, quantity, price) VALUES (?, ?, ?, ?)",
                  (name, category, quantity, price))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('add_item.html')

# =================== Update Item ===================
@app.route('/update_item/<int:id>', methods=['GET', 'POST'])
def update_item(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        c.execute("UPDATE items SET name=?, category=?, quantity=?, price=? WHERE id=?",
                  (name, category, quantity, price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    c.execute("SELECT * FROM items WHERE id=?", (id,))
    item = c.fetchone()
    conn.close()
    return render_template('update_item.html', item=item)

# =================== Delete Item ===================
@app.route('/delete_item/<int:id>')
def delete_item(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# =================== Run App ===================
if __name__ == '__main__':
    app.run(debug=True)
