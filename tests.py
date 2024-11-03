import mysql.connector  # Use mysql-connector-python

# Connection settings
config = {
    'user': 'root',          # Your database username
    'password': 'casaos',      # Your database password
    'host': 'db.lejk.net',            # Host address
    'database': 'OTOMOTO', # Database name
    'port': 3306                      # Port number, 3306 by default for MariaDB
}

# Establishing the connection
try:
    connection = mysql.connector.connect(**config)
    print("Connection successful!")
    
    # Your database interaction code here

finally:
    if connection.is_connected():
        connection.close()
        print("Connection closed.")