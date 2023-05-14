import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the Metadata table
new_cur.execute("""
SELECT MetaId, Name, Timestamp, Note, Value
FROM Metadata
ORDER BY Timestamp DESC
""")
metadata = new_cur.fetchall()

# Create a list of dictionaries representing the metadata
metadata_list = []
for row in metadata:
    metadata_list.append({
        "MetaId": row[0],
        "Name": row[1],
        "Timestamp": row[2],
        "Note": row[3],
        "Value": row[4]
    })

# Write the metadata to a JSON file
with open("Metadata.json", "w") as f:
    json.dump(metadata_list, f, indent=2)

# Close the new database
new_conn.close()