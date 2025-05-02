import sqlite3

def add_employee_id_column():
    # Connect to your SQLite database
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Add the new column to the sales table
    cursor.execute('ALTER TABLE sales ADD COLUMN employee_id INTEGER;')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Column 'employee_id' added to 'sales' table.")

# Call the function to add the column
add_employee_id_column()
