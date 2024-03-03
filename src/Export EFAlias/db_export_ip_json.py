import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the ClientInfo table sorted by DateAdded in descending order
new_cur.execute("""
SELECT Name, SearchableIPAddress, DateAdded FROM "IPAddresses"
ORDER BY DateAdded DESC
""")
client_info = new_cur.fetchall()

# Create a list of dictionaries representing the client info
client_info_list = []
for row in client_info:
    client_info_list.append({
        "Name": row[0],
        "SearchableIPAddress": row[1],
        "DateAdded": row[2]
    })

# Write the client info to a JSON file
with open("IPAddresses.json", "w") as f:
    json.dump(client_info_list, f, indent=2)

# Close the new database
new_conn.close()