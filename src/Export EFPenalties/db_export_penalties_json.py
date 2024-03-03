import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the Penalties table
new_cur.execute("""
SELECT PenaltyId, AutomatedOffense, Expires, EvadedOffense, Offender, Offense, Punisher, Type, Timestamp
FROM Penalties
ORDER BY Timestamp DESC
""")
penalties = new_cur.fetchall()

# Create a list of dictionaries representing the penalties
penalties_list = []
for row in penalties:
    penalties_list.append({
        "PenaltyId": row[0],
        "AutomatedOffense": row[1],
        "Expires": row[2],
        "EvadedOffense": row[3],
        "Offender": row[4],
        "Offense": row[5],
        "Punisher": row[6],
        "Type": row[7],
        "Timestamp": row[8]
    })

# Write the penalties to a JSON file
with open("Penalties.json", "w") as f:
    json.dump(penalties_list, f, indent=2)

# Close the new database
new_conn.close()