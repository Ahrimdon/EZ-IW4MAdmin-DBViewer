import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the Servers table
new_cur.execute("""
SELECT ServerId, Active, Port, Endpoint, Game, ServerName, Password
FROM Servers
""")
servers = new_cur.fetchall()

# Create a list of dictionaries representing the servers
servers_list = []
for row in servers:
    servers_list.append({
        "ServerId": row[0],
        "Active": row[1],
        "Port": row[2],
        "Endpoint": row[3],
        "Game": row[4],
        "ServerName": row[5],
        "Password": row[6]
    })

# Write the servers data to a JSON file
with open("Servers.json", "w") as f:
    json.dump(servers_list, f, indent=2)

# Close the new database
new_conn.close()