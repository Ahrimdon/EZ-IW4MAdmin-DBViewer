import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the ClientConnectionHistory table sorted by ConnectionTime in descending order
new_cur.execute("""
SELECT ConnectionId, Client, ConnectionTime, ConnectionType, Server
FROM ClientConnectionHistory
ORDER BY ConnectionTime DESC
""")
client_connection_history = new_cur.fetchall()

# Create a list of dictionaries representing the client connection history
client_connection_history_list = []
for row in client_connection_history:
    client_connection_history_list.append({
        "ConnectionId": row[0],
        "Client": row[1],
        "ConnectionTime": row[2],
        "ConnectionType": row[3],
        "Server": row[4]
    })

# Write the client connection history to a JSON file
with open("ClientConnectionHistory.json", "w") as f:
    json.dump(client_connection_history_list, f, indent=2)

# Close the new database
new_conn.close()
