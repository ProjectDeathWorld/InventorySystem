from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'inventory.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home Page with category-brand-product filters
@app.route('/')
def index():
    conn = get_db_connection()

    categories = conn.execute("SELECT id, name FROM categories").fetchall()
    brands = conn.execute("SELECT id, name, category_id FROM brands").fetchall()
    products = conn.execute("SELECT id, name, brand_id, price FROM products").fetchall()

    conn.close()
    return render_template('index.html', categories=categories, brands=brands, products=products)

@app.route('/get_brands/<int:category_id>')
def get_brands(category_id):
    conn = get_db_connection()
    brands = conn.execute("SELECT id, name FROM brands WHERE category_id = ?", (category_id,)).fetchall()
    conn.close()
    return jsonify([(brand['id'], brand['name']) for brand in brands])

@app.route('/get_products/<int:brand_id>')
def get_products(brand_id):
    conn = get_db_connection()
    products = conn.execute("SELECT id, name, price FROM products WHERE brand_id = ?", (brand_id,)).fetchall()
    conn.close()
    return jsonify([(product['id'], product['name'], product['price']) for product in products])

# (The rest of your routes stay unchanged below this line)

# View Customers
@app.route('/customers')
def view_customers():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

# (Rest of your routes and functions continue here unchanged)
# ...

# Run App
if __name__ == '__main__':
    app.run(debug=True)
