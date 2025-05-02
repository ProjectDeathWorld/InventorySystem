import sqlite3

# Connect to the database
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Delete the old payments table if it exists
cursor.execute("DROP TABLE IF EXISTS payments")

# Create a new payments table with sale_id
cursor.execute('''
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sale_id) REFERENCES sales(id)
    )
''')

# Save changes and close the connection
conn.commit()
conn.close()

print("Payments table recreated successfully with sale_id.")
