import sqlite3
import json

new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

new_cur.execute("""
SELECT PenaltyIdentifierId, PenaltyId, Created, Client
FROM PenaltyIdentifiers
ORDER BY Created DESC
""")
penalty_identifiers = new_cur.fetchall()

penalty_identifiers_list = []
for row in penalty_identifiers:
    penalty_identifiers_list.append({
        "PenaltyIdentifierId": row[0],
        "PenaltyId": row[1],
        "Created": row[2],
        "Client": row[3]
    })

with open("PenaltyIdentifiers.json", "w") as f:
    json.dump(penalty_identifiers_list, f, indent=2)
    
new_conn.close()