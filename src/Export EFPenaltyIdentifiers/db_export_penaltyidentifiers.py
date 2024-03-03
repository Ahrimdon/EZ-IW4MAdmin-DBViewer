import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified EFPenaltyIdentifiers table in the new database
new_cur.execute("""
CREATE TABLE "PenaltyIdentifiers" (
    "PenaltyIdentifierId" INTEGER NOT NULL,
    "PenaltyId" INTEGER NOT NULL,
    "Created" TEXT NOT NULL,
    "Client" TEXT NOT NULL
)
""")

existing_cur.execute("""
SELECT
    EFPenaltyIdentifiers.PenaltyIdentifierId,
    EFPenaltyIdentifiers.PenaltyId,
    EFPenaltyIdentifiers.CreatedDateTime,
    EFPenaltyIdentifiers.NetworkId
FROM
    EFPenaltyIdentifiers
""")
rows = existing_cur.fetchall()

for row in rows:
    penalty_identifier_id = row[0]
    penalty_id = row[1]
    created = row[2]
    network_id = row[3]

    
    existing_cur.execute("""
    SELECT
        EFAlias.Name
    FROM
        EFAlias
    INNER JOIN
        EFClients ON EFAlias.AliasId = EFClients.CurrentAliasId
    WHERE
        EFClients.NetworkId = ?
    """, (network_id,))
    client_name = existing_cur.fetchone()
    if client_name:
        client_name = client_name[0].replace('^7', '')
    else:
        client_name = 'Unknown'

    
    new_cur.execute("""
    INSERT INTO PenaltyIdentifiers (
        PenaltyIdentifierId,
        PenaltyId,
        Created,
        Client
    )
    VALUES (?, ?, ?, ?)
    """, (penalty_identifier_id, penalty_id, created, client_name))

# Commit changes and close the new database
new_conn.commit()
new_conn.close()

# Close the existing database
existing_conn.close()