import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Fetch data from the InboxMessagesModified table
new_cur.execute("""
SELECT InboxMessageId, Created, Origin, Target, ServerId, Message, Read
FROM InboxMessagesModified
ORDER BY Created DESC
""")
inbox_messages = new_cur.fetchall()

# Create a list of dictionaries representing the inbox messages
inbox_messages_list = []
for row in inbox_messages:
    inbox_messages_list.append({
        "InboxMessageId": row[0],
        "Created": row[1],
        "Origin": row[2],
        "Target": row[3],
        "ServerId": row[4],
        "Message": row[5],
        "Read": row[6]
    })

# Write the inbox messages to a JSON file
with open("InboxMessages.json", "w") as f:
    json.dump(inbox_messages_list, f, indent=2)

# Close the new database
new_conn.close()