# EFServers

import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified Servers table in the new database
new_cur.execute("""
CREATE TABLE "Servers" (
    "ServerId" INTEGER NOT NULL,
    "Active" INTEGER NOT NULL,
    "Port" INTEGER NOT NULL,
    "Endpoint" TEXT NOT NULL,
    "Game" TEXT NOT NULL,
    "ServerName" TEXT NOT NULL,
    "Password" TEXT NOT NULL
)
""")

# Fetch data from existing EFServers
existing_cur.execute("""
SELECT ServerId, Active, Port, Endpoint, GameName, HostName, IsPasswordProtected
FROM EFServers
""")
rows = existing_cur.fetchall()

# Define the game name mapping
game_mapping = {5: "WaW", 7: "BO2", 6: "BO", 3: "MW3"}

for row in rows:
    server_id = row[0]
    active = row[1]
    port = row[2]
    endpoint = row[3]
    game_name = row[4]
    server_name = row[5]
    is_password_protected = row[6]

    # Replace the game_name with corresponding text
    game_name = game_mapping.get(game_name, game_name)

    # Replace the IsPasswordProtected values with 'Yes' or 'No'
    password = "Yes" if is_password_protected == 1 else "No"

    # Insert the modified row into the new Servers table
    new_cur.execute("""
    INSERT INTO Servers (
        ServerId,
        Active,
        Port,
        Endpoint,
        Game,
        ServerName,
        Password
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (server_id, active, port, endpoint, game_name, server_name, password))

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()