# EFMaps

import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the Maps table in the new_database.db
new_cur.execute("""
CREATE TABLE IF NOT EXISTS "Maps" (
    "MapId" INTEGER NOT NULL,
    "CreatedDateTime" TEXT NOT NULL,
    "Name" TEXT NOT NULL,
    "Game" TEXT NOT NULL,
    CONSTRAINT "PK_Maps" PRIMARY KEY("MapId" AUTOINCREMENT)
)
""")

# Fetch data from the existing EFMaps table
existing_cur.execute("""
SELECT
    MapId, CreatedDateTime, Name, Game
FROM
    EFMaps
""")
rows = existing_cur.fetchall()

# Modify the data according to the requirements
modified_rows = []
for row in rows:
    game_map = {5: "WaW", 6: "BO", 7: "BO2", 3: "MW3"}
    game = game_map.get(row[3], f"Unknown Game ({row[3]})")
    modified_rows.append((row[0], row[1], row[2], game))

# Insert the modified data into the Maps table in the new_database.db
new_cur.executemany("""
INSERT INTO "Maps" (
    MapId, CreatedDateTime, Name, Game
) VALUES (?, ?, ?, ?)
""", modified_rows)

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()