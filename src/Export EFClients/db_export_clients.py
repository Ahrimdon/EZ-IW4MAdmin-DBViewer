# EFClients

import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

new_cur.execute("""
CREATE TABLE "Clients" (
    "Connections" INTEGER NOT NULL,
    "Name" TEXT NOT NULL,
    "FirstConnection" TEXT NOT NULL,
    "Game" TEXT NOT NULL,
    "LastConnection" TEXT NOT NULL,
    "Level" TEXT NOT NULL,
    "Masked" INTEGER NOT NULL,
    "TotalConnectionTime" INTEGER NOT NULL,
    "IP" TEXT
)
""")

existing_cur.execute("""
SELECT
    EFClients.Connections,
    EFClients.CurrentAliasId,
    EFClients.FirstConnection,
    EFClients.GameName,
    EFClients.LastConnection,
    EFClients.Level,
    EFClients.Masked,
    EFClients.TotalConnectionTime,
    EFAlias.SearchableIPAddress
FROM
    EFClients
JOIN
    EFAlias ON EFClients.CurrentAliasId = EFAlias.AliasId
""")
rows = existing_cur.fetchall()

for row in rows:
    connections = row[0]
    current_alias_id = row[1]
    first_connection = row[2]
    game_name = row[3]
    last_connection = row[4]
    level = row[5]
    masked = row[6]
    total_connection_time = row[7]
    ip_address = row[8]

    # Retrieve client name
    existing_cur.execute("""
    SELECT
        EFAlias.Name
    FROM
        EFAlias
    WHERE
        EFAlias.AliasId = ?
    """, (current_alias_id,))
    client_name = existing_cur.fetchone()
    if client_name:
        client_name = client_name[0].replace('^7', '')
    else:
        client_name = 'Unknown'

    # Map Level values to their corresponding text
    level_map = {-1: "Banned", 0: "User", 1: "Trusted", 2: "Moderator", 3: "Administrator", 4: "Senior Administrator", 5: "Owner", 6: "Creator", 7: "Console"}
    level = level_map.get(level, f"Unknown Level ({level})")

    # Map GameName values to their corresponding text
    game_map = {5: "WaW", 6: "BO", 7: "BO2", 3: "MW3"}
    game = game_map.get(game_name, f"Unknown Game ({game_name})")

    # Insert the modified row into the new Clients table
    new_row = (connections, client_name, first_connection, game, last_connection, level, masked, total_connection_time, ip_address)
    new_cur.execute("INSERT INTO Clients (Connections, Name, FirstConnection, Game, LastConnection, Level, Masked, TotalConnectionTime, IP) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", new_row)

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()