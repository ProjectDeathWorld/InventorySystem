from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'inventory.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home Page
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.*, c.name as category, s.name as supplier, b.name as brand
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN brands b ON p.brand_id = b.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# View Customers
@app.route('/customers')
def view_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('view_customers.html', customers=customers)

# View Suppliers
@app.route('/suppliers')
def view_suppliers():
    conn = get_db_connection()
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    conn.close()
    return render_template('view_suppliers.html', suppliers=suppliers)

# View Categories
@app.route('/categories')
def view_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

# View Brands
@app.route('/brands')
def view_brands():
    conn = get_db_connection()
    brands = conn.execute('SELECT * FROM brands').fetchall()
    conn.close()
    return render_template('brands.html', brands=brands)

# View Employees
@app.route('/employees')
def view_employees():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return render_template('employees.html', employees=employees)

# Record Sale with Sale_Items
@app.route('/sale', methods=['GET', 'POST'])
def record_sale():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    customers = conn.execute('SELECT * FROM customers').fetchall()

    if request.method == 'POST':
        customer_id = int(request.form['customer_id'])
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        employee_id = int(request.form['employee_id'])  # Assuming logged-in employee or selected manually

        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        total_price = quantity * product['price']

        # Insert into sales
        conn.execute('''
            INSERT INTO sales (customer_id, employee_id, sale_date)
            VALUES (?, ?, ?)
        ''', (customer_id, employee_id, datetime.now()))
        sale_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        # Insert into sale_items
        conn.execute('''
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
        ''', (sale_id, product_id, quantity, product['price']))

        # Decrease inventory
        conn.execute('''
            UPDATE products SET stock = stock - ?
            WHERE id = ?
        ''', (quantity, product_id))

        # Insert payment
        conn.execute('''
            INSERT INTO payments (sale_id, amount, payment_date)
            VALUES (?, ?, ?)
        ''', (sale_id, total_price, datetime.now()))

        # Log inventory movement
        conn.execute('''
            INSERT INTO inventory_logs (product_id, quantity, action, date)
            VALUES (?, ?, ?, ?)
        ''', (product_id, -quantity, 'sale', datetime.now()))

        conn.commit()
        conn.close()
        return redirect(url_for('view_sales'))

    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return render_template('record_sale.html', products=products, customers=customers, employees=employees)

# View Sales
@app.route('/sales')
def view_sales():
    conn = get_db_connection()
    sales = conn.execute('''
        SELECT sales.id, customers.name AS customer, employees.name AS employee, sales.sale_date
        FROM sales
        LEFT JOIN customers ON sales.customer_id = customers.id
        LEFT JOIN employees ON sales.employee_id = employees.id
        ORDER BY sales.sale_date DESC
    ''').fetchall()
    conn.close()
    return render_template('sales.html', sales=sales)

# View Sale Items
@app.route('/sale_items')
def view_sale_items():
    conn = get_db_connection()
    sale_items = conn.execute('''
        SELECT si.id, s.id AS sale_id, p.name AS product, si.quantity, si.unit_price
        FROM sale_items si
        JOIN sales s ON si.sale_id = s.id
        JOIN products p ON si.product_id = p.id
    ''').fetchall()
    conn.close()
    return render_template('sale_items.html', sale_items=sale_items)

# View Payments
@app.route('/payments')
def view_payments():
    conn = get_db_connection()
    payments = conn.execute('''
        SELECT p.id, s.id AS sale_id, p.amount, p.payment_date
        FROM payments p
        JOIN sales s ON p.sale_id = s.id
    ''').fetchall()
    conn.close()
    return render_template('payments.html', payments=payments)

# View Inventory Logs
@app.route('/inventory_logs')
def view_inventory_logs():
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT l.id, p.name AS product, l.quantity, l.action, l.date
        FROM inventory_logs l
        JOIN products p ON l.product_id = p.id
        ORDER BY l.date DESC
    ''').fetchall()
    conn.close()
    return render_template('inventory_logs.html', logs=logs)

# Add Product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        cost_price = float(request.form['cost_price'])
        category_id = int(request.form['category_id'])
        supplier_id = int(request.form['supplier_id'])
        brand_id = int(request.form['brand_id'])

        conn.execute('''
            INSERT INTO products (name, price, stock, cost_price, category_id, supplier_id, brand_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, price, stock, cost_price, category_id, supplier_id, brand_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    categories = conn.execute('SELECT * FROM categories').fetchall()
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    brands = conn.execute('SELECT * FROM brands').fetchall()
    conn.close()
    return render_template('add_product.html', categories=categories, suppliers=suppliers, brands=brands)

# Edit Product
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        cost_price = float(request.form['cost_price'])
        category_id = int(request.form['category_id'])
        supplier_id = int(request.form['supplier_id'])
        brand_id = int(request.form['brand_id'])

        conn.execute('''
            UPDATE products
            SET name=?, price=?, stock=?, cost_price=?, category_id=?, supplier_id=?, brand_id=?
            WHERE id=?
        ''', (name, price, stock, cost_price, category_id, supplier_id, brand_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    suppliers = conn.execute('SELECT * FROM suppliers').fetchall()
    brands = conn.execute('SELECT * FROM brands').fetchall()
    conn.close()
    return render_template('edit_product.html', product=product, categories=categories, suppliers=suppliers, brands=brands)

@app.route('/record_sale', methods=['GET', 'POST'])
def record_sale():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        # Handle sale creation, add customer_id to your INSERT

        conn.execute('INSERT INTO sales (sale_date, customer_id) VALUES (?, ?)',
                     (datetime.now().strftime('%Y-%m-%d'), customer_id))
        conn.commit()
        conn.close()
        return redirect('/sales')

    # For GET request - get customers
    customers = conn.execute('SELECT id, name FROM customers').fetchall()
    conn.close()
    return render_template('record_sale.html', customers=customers)

@app.route('/sales')
def view_sales():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sales = cursor.execute('''
        SELECT 
            sales.id,
            customers.name AS customer_name,
            products.name AS product_name,
            sale_items.quantity,
            sales.sale_date
        FROM sales
        JOIN customers ON sales.customer_id = customers.id
        JOIN sale_items ON sales.id = sale_items.sale_id
        JOIN products ON sale_items.product_id = products.id
        ORDER BY sales.sale_date DESC
    ''').fetchall()
    conn.close()

    return render_template('sales.html', sales=sales)

# Run App
if __name__ == '__main__':
    app.run(debug=True)
