import sqlite3

def create_inventory_logs_table():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create the inventory_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        action TEXT NOT NULL,  -- 'sale' or 'restock'
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    conn.commit()
    conn.close()

# Call the function to create the table
create_inventory_logs_table()
