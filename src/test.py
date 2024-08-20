import sqlite3

# Connect to the database
conn = sqlite3.connect('database/todo.db')
cursor = conn.cursor()

# Execute a query
cursor.execute("SELECT * FROM todo;")
rows = cursor.fetchall()

print(type(rows))

# Print the results
for row in rows:
    print(row)

# Close the connection
conn.close()