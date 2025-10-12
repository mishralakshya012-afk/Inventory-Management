from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'inventory.db'

# ---------------- Helper ----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- Initialize ----------------
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )''')

        # Items table
        c.execute('''CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        price REAL DEFAULT 0
                    )''')
        conn.commit()


# ---------------- Routes ----------------
@app.route('/')
def about():
    """Landing page"""
    return render_template('about.html')


@app.route('/home')
def home():
    """Home page"""
    return render_template('index.html')


# -------- Register --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()  # Clear any existing session

    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('⚠️ Passwords do not match!')
            return redirect(url_for('register'))

        with get_db_connection() as conn:
            existing_user = conn.execute(
                'SELECT * FROM users WHERE username = ? OR email = ?',
                (username, email)
            ).fetchone()

            if existing_user:
                flash('⚠️ Username or Email already exists!')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()

        flash('✅ Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


# -------- Login --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'👋 Welcome back, {user["username"]}!')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid username or password!')
            return redirect(url_for('login'))

    return render_template('login.html')


# -------- Logout --------
@app.route('/logout')
def logout():
    session.clear()
    flash('✅ Logged out successfully!')
    return redirect(url_for('login'))


# -------- Dashboard --------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!')
        return redirect(url_for('login'))

    category_filter = request.args.get('category', 'All')
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'name')

    conn = get_db_connection()
    categories = conn.execute("SELECT DISTINCT category FROM items").fetchall()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if category_filter != 'All':
        query += " AND category = ?"
        params.append(category_filter)

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    valid_sort_fields = ['name', 'price', 'quantity', 'category']
    if sort_by not in valid_sort_fields:
        sort_by = 'name'

    query += f" ORDER BY {sort_by}"

    items = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'dashboard.html',
        items=items,
        categories=categories,
        selected_category=category_filter,
        search_query=search_query,
        sort_by=sort_by
    )


# -------- Add Item --------
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        quantity = request.form['quantity']
        category = request.form['category'].strip()
        price = request.form['price']

        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO items (name, quantity, category, price) VALUES (?, ?, ?, ?)',
                (name, quantity, category, price)
            )
            conn.commit()

        flash('✅ Item added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('add_item.html')


# -------- Update Item --------
@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()

        if not item:
            flash('❌ Item not found!')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            name = request.form['name']
            quantity = request.form['quantity']
            category = request.form['category']
            price = request.form['price']

            conn.execute(
                'UPDATE items SET name=?, quantity=?, category=?, price=? WHERE id=?',
                (name, quantity, category, price, item_id)
            )
            conn.commit()

            flash('✅ Item updated successfully!')
            return redirect(url_for('dashboard'))

    return render_template('update_item.html', item=item)


# -------- Delete Item --------
@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
        conn.commit()

    flash('🗑️ Item deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    if 'user_id' not in session:
        flash('Please login first!')
        return redirect(url_for('login'))

    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = {}

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()

    if not item:
        flash('Item not found!')
        return redirect(url_for('dashboard'))

    cart = session['cart']
    item_id_str = str(item_id)

    # Add only once by default
    if item_id_str not in cart:
        cart[item_id_str] = {
            'id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': 1
        }
        flash(f"{item['name']} added to cart.")
    else:
        flash(f"{item['name']} is already in your cart!")

    session['cart'] = cart
    return redirect(url_for('dashboard'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)

    cart_items = list(session['cart'].values())
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:item_id>/<action>')
def update_cart(item_id, action):
    if 'cart' not in session:
        return redirect(url_for('cart'))

    cart = session['cart']
    item_id_str = str(item_id)

    if item_id_str in cart:
        if action == 'increase':
            cart[item_id_str]['quantity'] += 1
        elif action == 'decrease':
            cart[item_id_str]['quantity'] -= 1
            if cart[item_id_str]['quantity'] <= 0:
                del cart[item_id_str]
                flash('Item removed from cart!')
        session['cart'] = cart

    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    if 'cart' in session:
        cart = session['cart']
        item_id_str = str(item_id)
        if item_id_str in cart:
            del cart[item_id_str]
            session['cart'] = cart
            flash('Item removed from cart!')
    return redirect(url_for('cart'))

@app.route('/generate_bill')
def generate_bill():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!')
        return redirect(url_for('cart'))

    cart = session['cart']
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    return render_template('bill.html', cart_items=cart.values(), total=total)

# -------- Main --------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, threaded=True)
