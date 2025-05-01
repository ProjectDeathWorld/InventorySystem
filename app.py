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
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        cost_price = float(request.form['cost_price'])
        category_id = int(request.form['category_id'])
        supplier_id = int(request.form['supplier_id'])

        conn.execute('''
            INSERT INTO products (name, description, price, stock, cost_price, category_id, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, price, stock, cost_price, category_id, supplier_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    categories = conn.execute('SELECT * FROM categories').fetchall()
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    conn.close()
    return render_template('add_product.html', categories=categories, suppliers=suppliers)

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
        cost_price = float(request.form['cost_price'])
        category_id = int(request.form['category_id'])
        supplier_id = int(request.form['supplier_id'])

        conn.execute('''
            UPDATE products SET name = ?, description = ?, price = ?, stock = ?, cost_price = ?, category_id = ?, supplier_id = ?
            WHERE id = ?
        ''', (name, description, price, stock, cost_price, category_id, supplier_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    categories = conn.execute('SELECT * FROM categories').fetchall()
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    conn.close()
    return render_template('edit_product.html', product=product, categories=categories, suppliers=suppliers)

# Record Sale
@app.route('/sale', methods=['GET', 'POST'])
def record_sale():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    customers = conn.execute('SELECT * FROM customers').fetchall()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        customer_id = int(request.form['customer_id'])
        quantity = int(request.form['quantity'])

        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        cost_price = product['cost_price']
        selling_price = product['price']

        selling_total = selling_price * quantity
        cost_total = cost_price * quantity
        profit = selling_total - cost_total

        conn.execute('''
            INSERT INTO sales (product_id, customer_id, quantity) 
            VALUES (?, ?, ?)
        ''', (product_id, customer_id, quantity))

        sale_id = conn.lastrowid
        conn.execute('''
            INSERT INTO profit (sale_id, cost_price_total, selling_price_total, profit_amount)
            VALUES (?, ?, ?, ?)
        ''', (sale_id, cost_total, selling_total, profit))

        conn.execute('''
            UPDATE products SET stock = stock - ? WHERE id = ?
        ''', (quantity, product_id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_sales'))

    conn.close()
    return render_template('record_sale.html', products=products, customers=customers)

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

# View Profit Report
@app.route('/profit')
def view_profit():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM profit')
    profits = cur.fetchall()

    cur.execute('SELECT SUM(profit_amount) FROM profit')
    total_profit = cur.fetchone()[0] or 0

    conn.close()
    return render_template('profit.html', profits=profits, total_profit=total_profit)

# Add Customer Route
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        conn = get_db_connection()
        conn.execute('INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                     (name, email, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_customer.html')

# View Customers
@app.route('/view_customers')
def view_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('view_customers.html', customers=customers)

@app.route('/categories')
def view_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/suppliers')
def view_suppliers():
    conn = get_db_connection()
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    conn.close()
    return render_template('view_suppliers.html', suppliers=suppliers)


# Run App
if __name__ == '__main__':
    app.run(debug=True)
