import sqlite3
import json

# Connect to the new database
new_conn = sqlite3.connect("Database.db")
new_cur = new_conn.cursor()

# Fetch data from the EFChangeHistory table sorted by Time in descending order
new_cur.execute("""
SELECT ChangeHistoryId, TypeOfChange, Time, Data, Command, Origin, Target FROM AuditLog
ORDER BY Time DESC
""")
ef_change_history = new_cur.fetchall()

# Create a list of dictionaries representing the EFChangeHistory data
ef_change_history_list = []
for row in ef_change_history:
    ef_change_history_list.append({
        "ChangeHistoryId": row[0],
        "TypeOfChange": row[1],
        "Time": row[2],
        "Data": row[3],
        "Command": row[4],
        "Origin": row[5],
        "Target": row[6]
    })

# Write the EFChangeHistory data to a JSON file
with open("AuditLog.json", "w") as f:
    json.dump(ef_change_history_list, f, indent=2)

# Close the new database
new_conn.close()
