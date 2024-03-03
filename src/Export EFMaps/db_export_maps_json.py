import sqlite3
import json

# Connect to the new_database.db
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the Maps table sorted by MapId DESC
new_cur.execute("""
SELECT
    MapId, CreatedDateTime, Name, Game
FROM
    Maps
ORDER BY
    MapId DESC
""")
rows = new_cur.fetchall()

# Convert fetched data into a list of dictionaries
maps_list = []
for row in rows:
    map_dict = {
        "MapId": row[0],
        "CreatedDateTime": row[1],
        "Name": row[2],
        "Game": row[3]
    }
    maps_list.append(map_dict)

# Write the list of dictionaries to a JSON file
with open("maps_export.json", "w") as json_file:
    json.dump(maps_list, json_file, indent=4)

# Close the connection
new_conn.close()