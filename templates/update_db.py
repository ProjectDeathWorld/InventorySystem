import sqlite3

# Connect to the database
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Add the missing columns
cursor.execute("ALTER TABLE products ADD COLUMN category_id INTEGER")
cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Columns added successfully!")
