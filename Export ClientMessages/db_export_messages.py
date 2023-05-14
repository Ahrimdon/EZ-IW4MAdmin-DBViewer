import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified ClientMessages table in the new database
new_cur.execute("""
CREATE TABLE "ClientMessages" (
    "MessageId" INTEGER NOT NULL,
    "Client" TEXT NOT NULL,
    "Message" TEXT NOT NULL,
    "TimeSent" TEXT NOT NULL,
    "Server" TEXT,
    CONSTRAINT "PK_ClientMessages" PRIMARY KEY("MessageId" AUTOINCREMENT)
)
""")

# Fetch data from existing EFClientMessages
existing_cur.execute("""
SELECT
    EFClientMessages.MessageId,
    EFClientMessages.ClientId,
    EFClientMessages.Message,
    EFClientMessages.TimeSent,
    EFClientMessages.ServerId
FROM
    EFClientMessages
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

    # Insert the modified row into the new ClientMessages table
    new_row = (row[0], client_name, row[2], row[3], server_hostname)
    new_cur.execute("INSERT INTO ClientMessages (MessageId, Client, Message, TimeSent, Server) VALUES (?, ?, ?, ?, ?)", new_row)

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()