from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'inventory.db'

# Connect to database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home - List all products
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Add Product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)',
                     (name, description, price, stock))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_product.html')

# Edit Product
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        conn.execute('UPDATE products SET name = ?, description = ?, price = ?, stock = ? WHERE id = ?',
                     (name, description, price, stock, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_product.html', product=product)

# Delete Product
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Record Sale
@app.route('/sale', methods=['GET', 'POST'])
def record_sale():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])

        conn.execute('INSERT INTO sales (product_id, quantity) VALUES (?, ?)', (product_id, quantity))
        conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (quantity, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_sales'))

    conn.close()
    return render_template('record_sale.html', products=products)

# View Sales History
@app.route('/sales')
def view_sales():
    conn = get_db_connection()
    sales = conn.execute('''
        SELECT sales.id, products.name AS product_name, sales.quantity, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.sale_date DESC
    ''').fetchall()
    conn.close()
    return render_template('sales.html', sales=sales)

# Add Customer
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        conn = get_db_connection()
        conn.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('view_customers'))
    return render_template('add_customer.html')

# View Customers
@app.route('/view_customers')
def view_customers():
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return render_template('view_customers.html', customers=customers)

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("INSERT INTO suppliers (name, contact, address) VALUES (?, ?, ?)", (name, contact, address))
        conn.commit()
        conn.close()
        return redirect('/suppliers')
    return render_template('add_supplier.html')

@app.route('/suppliers')
def view_suppliers():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM suppliers")
    suppliers = c.fetchall()
    conn.close()
    return render_template('view_suppliers.html', suppliers=suppliers)

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        category_name = request.form['name']
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # category already exists
    
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    conn.close()
    
    return render_template('categories.html', categories=categories)

@app.route('/profit')
def view_profit():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Profit")
    profits = cur.fetchall()
    conn.close()
    return render_template('profit.html', profits=profits)

@app.route('/profit')
def profit_report():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Profit")
    profits = cur.fetchall()

    cur.execute("SELECT SUM(profit_amount) FROM Profit")
    total_profit = cur.fetchone()[0] or 0
    conn.close()

    return render_template("profit.html", profits=profits, total_profit=round(total_profit, 2))

@app.route('/record_sale', methods=['POST'])
def record_sale():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])

    conn = sqlite3.connect('inventory.db')
    cur = conn.cursor()

    # Get product price and cost
    cur.execute("SELECT price, cost_price FROM Products WHERE id = ?", (product_id,))
    result = cur.fetchone()
    selling_price = result[0]
    cost_price = result[1]

    selling_total = selling_price * quantity
    cost_total = cost_price * quantity

    # Insert into Sales table
    cur.execute("INSERT INTO Sales (product_id, quantity, sale_date) VALUES (?, ?, date('now'))", (product_id, quantity))
    sale_id = cur.lastrowid

    # Insert into Profit table
    cur.execute("INSERT INTO Profit (sale_id, cost_price_total, selling_price_total) VALUES (?, ?, ?)",
                (sale_id, cost_total, selling_total))

    # Update stock
    cur.execute("UPDATE Products SET stock = stock - ? WHERE id = ?", (quantity, product_id))

    conn.commit()
    conn.close()
    return redirect('/sales')

# Run App
if __name__ == '__main__':
    app.run(debug=True)

