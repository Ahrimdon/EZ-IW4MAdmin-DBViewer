import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified ClientConnectionHistory table in the new database
new_cur.execute("""
CREATE TABLE "ClientConnectionHistory" (
    "ConnectionId" INTEGER NOT NULL,
    "Client" TEXT NOT NULL,
    "ConnectionTime" TEXT NOT NULL,
    "ConnectionType" TEXT NOT NULL,
    "Server" TEXT,
    CONSTRAINT "PK_ClientConnectionHistory" PRIMARY KEY("ConnectionId" AUTOINCREMENT)
)
""")

# Fetch data from existing EFClientConnectionHistory
existing_cur.execute("""
SELECT
    EFClientConnectionHistory.ClientConnectionId,
    EFClientConnectionHistory.ClientId,
    EFClientConnectionHistory.CreatedDateTime,
    EFClientConnectionHistory.ConnectionType,
    EFClientConnectionHistory.ServerId
FROM
    EFClientConnectionHistory
""")
rows = existing_cur.fetchall()

for row in rows:
    client_id = row[1]
    server_id = row[4]

    # Retrieve client name
    existing_cur.execute("""
    SELECT
        EFAlias.Name
    FROM
        EFClients
    JOIN EFAlias ON EFClients.CurrentAliasId = EFAlias.AliasId
    WHERE
        EFClients.ClientId = ?
    """, (client_id,))
    client_name = existing_cur.fetchone()
    if client_name:
        client_name = client_name[0].replace('^7', '')
    else:
        client_name = 'Unknown'

    # Retrieve server hostname
    existing_cur.execute("""
    SELECT
        EFServers.HostName
    FROM
        EFServers
    WHERE
        EFServers.ServerId = ?
    """, (server_id,))
    server_hostname = existing_cur.fetchone()
    if server_hostname:
        server_hostname = server_hostname[0]
    else:
        server_hostname = 'Unknown'

    # Map ConnectionType values to their corresponding text
    connection_type_map = {0: "Connect", 1: "Disconnect"}
    connection_type = connection_type_map[row[3]]

    # Insert the modified row into the new ClientConnectionHistory table
    new_row = (row[0], client_name, row[2], connection_type, server_hostname)
    new_cur.execute("INSERT INTO ClientConnectionHistory (ConnectionId, Client, ConnectionTime, ConnectionType, Server) VALUES (?, ?, ?, ?, ?)", new_row)

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()