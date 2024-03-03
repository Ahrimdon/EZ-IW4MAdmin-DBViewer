import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the EFClients table
new_cur.execute("""
SELECT Connections, Name, FirstConnection, Game, LastConnection, Level, Masked, TotalConnectionTime
FROM Clients
ORDER BY LastConnection DESC
""")
clients = new_cur.fetchall()

# Create a list of dictionaries representing the clients
clients_list = []
for row in clients:
    clients_list.append({
        "Connections": row[0],
        "Name": row[1],
        "FirstConnection": row[2],
        "Game": row[3],
        "LastConnection": row[4],
        "Level": row[5],
        "Masked": row[6],
        "TotalConnectionTime": row[7]
    })

# Write the clients to a JSON file
with open("Clients.json", "w") as f:
    json.dump(clients_list, f, indent=2)

# Close the new database
new_conn.close()