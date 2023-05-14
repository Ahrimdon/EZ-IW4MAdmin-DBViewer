import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the ClientMessages table
new_cur.execute("""
SELECT MessageId, Client, Message, TimeSent, Server
FROM ClientMessages
ORDER BY TimeSent DESC
""")
client_messages = new_cur.fetchall()

# Create a list of dictionaries representing the client messages
client_messages_list = []
for row in client_messages:
    client_messages_list.append({
        "MessageId": row[0],
        "Client": row[1],
        "Message": row[2],
        "TimeSent": row[3],
        "Server": row[4]
    })

# Write the client messages to a JSON file
with open("ClientMessages.json", "w") as f:
    json.dump(client_messages_list, f, indent=2)

# Close the new database
new_conn.close()
