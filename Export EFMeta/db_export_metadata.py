# EFMeta

import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified Metadata table in the new database
new_cur.execute("""
CREATE TABLE "Metadata" (
    "MetaId" INTEGER NOT NULL,
    "Name" TEXT NOT NULL,
    "Timestamp" TEXT NOT NULL,
    "Note" TEXT NOT NULL,
    "Value" TEXT NOT NULL
)
""")

# Fetch data from existing EFMeta
existing_cur.execute("""
SELECT
    EFMeta.MetaId,
    EFMeta.ClientId,
    EFMeta.Created,
    EFMeta.Key,
    EFMeta.Value
FROM
    EFMeta
""")
rows = existing_cur.fetchall()

for row in rows:
    meta_id = row[0]
    client_id = row[1]
    created = row[2]
    key = row[3]
    value = row[4]

    # Retrieve CurrentAliasId for the ClientId
    existing_cur.execute("""
    SELECT
        EFClients.CurrentAliasId
    FROM
        EFClients
    WHERE
        EFClients.ClientId = ?
    """, (client_id,))
    current_alias_id = existing_cur.fetchone()
    if current_alias_id:
        current_alias_id = current_alias_id[0]
    else:
        current_alias_id = None

    # Retrieve client name
    if current_alias_id:
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
    else:
        client_name = 'Unknown'

    # Insert the modified row into the new Metadata table
    new_row = (meta_id, client_name, created, key, value)
    new_cur.execute("INSERT INTO Metadata (MetaId, Name, Timestamp, Note, Value) VALUES (?, ?, ?, ?, ?)", new_row)

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()