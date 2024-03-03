import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified AuditLog table in the new database
new_cur.execute("""
CREATE TABLE "AuditLog" (
    "ChangeHistoryId" INTEGER NOT NULL,
    "TypeOfChange" TEXT NOT NULL,
    "Time" TEXT NOT NULL,
    "Data" TEXT,
    "Command" TEXT,
    "Origin" TEXT,
    "Target" TEXT,
    CONSTRAINT "PK_AuditLog" PRIMARY KEY("ChangeHistoryId" AUTOINCREMENT)
)
""")

# Fetch data from existing EFChangeHistory, EFClients, and EFAlias tables
existing_cur.execute("""
SELECT
    EFChangeHistory.ChangeHistoryId,
    EFChangeHistory.TypeOfChange,
    EFChangeHistory.TimeChanged,
    EFChangeHistory.Comment,
    EFChangeHistory.CurrentValue,
    EFChangeHistory.OriginEntityId,
    EFChangeHistory.TargetEntityId
FROM
    EFChangeHistory
""")
rows = existing_cur.fetchall()

# Prepare a dictionary to store ClientId to Name mapping
client_name_map = {}

for row in rows:
    origin_entity_id = row[5]
    target_entity_id = row[6]
    
    if origin_entity_id not in client_name_map:
        existing_cur.execute("""
        SELECT
            EFAlias.Name
        FROM
            EFClients
        JOIN EFAlias ON EFClients.CurrentAliasId = EFAlias.AliasId
        WHERE
            EFClients.ClientId = ?
        """, (origin_entity_id,))
        origin_name = existing_cur.fetchone()
        if origin_name:
            client_name_map[origin_entity_id] = origin_name[0].replace('^7', '')
        else:
            client_name_map[origin_entity_id] = 'Unknown'
    
    if target_entity_id not in client_name_map:
        if target_entity_id == 0:
            client_name_map[target_entity_id] = None
        else:
            existing_cur.execute("""
            SELECT
                EFAlias.Name
            FROM
                EFClients
            JOIN EFAlias ON EFClients.CurrentAliasId = EFAlias.AliasId
            WHERE
                EFClients.ClientId = ?
            """, (target_entity_id,))
            target_name = existing_cur.fetchone()
            if target_name:
                client_name_map[target_entity_id] = target_name[0].replace('^7', '')
            else:
                client_name_map[target_entity_id] = 'Unknown'

    # Map TypeOfChange values to their corresponding text
    type_of_change_map = {0: "Console", 1: "Punishment", 2: "Client"}
    type_of_change = type_of_change_map[row[1]]

    # Insert the modified row into the new AuditLog table
    new_row = (row[0], type_of_change, row[2], row[3], row[4], client_name_map[origin_entity_id], client_name_map[target_entity_id])
    new_cur.execute("INSERT INTO \"AuditLog\" (ChangeHistoryId, TypeOfChange, Time, Data, Command, Origin, Target) VALUES (?, ?, ?, ?, ?, ?, ?)", new_row)

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()