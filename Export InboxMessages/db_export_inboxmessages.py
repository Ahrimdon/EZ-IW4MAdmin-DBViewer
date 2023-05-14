import sqlite3

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Create a new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the new InboxMessagesModified table
new_cur.execute("""
CREATE TABLE InboxMessagesModified (
    InboxMessageId INTEGER PRIMARY KEY,
    Created TEXT,
    Origin TEXT,
    Target TEXT,
    ServerId INTEGER,
    Message TEXT,
    Read TEXT
)
""")

# Fetch data from the InboxMessages table
existing_cur.execute("SELECT * FROM InboxMessages")
inbox_messages = existing_cur.fetchall()

# Iterate through the InboxMessages and insert modified data into the new table
for msg in inbox_messages:
    msg_id, created, _, source_client_id, dest_client_id, server_id, message, is_delivered = msg

    # Find the SourceClientId and DestinationClientId names
    for client_id in (source_client_id, dest_client_id):
        existing_cur.execute("SELECT CurrentAliasId FROM EFClients WHERE ClientId = ?", (client_id,))
        alias_id = existing_cur.fetchone()[0]
        existing_cur.execute("SELECT Name FROM EFAlias WHERE AliasId = ?", (alias_id,))
        name = existing_cur.fetchone()[0].replace('^7', '')

        if client_id == source_client_id:
            origin = name
        else:
            target = name

    # Update Read status
    read = "Yes" if is_delivered == 1 else "No"

    # Insert the modified data into the new table
    new_cur.execute("""
    INSERT INTO InboxMessagesModified (InboxMessageId, Created, Origin, Target, ServerId, Message, Read)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (msg_id, created, origin, target, server_id, message, read))

# Commit the changes and close the connections
new_conn.commit()
existing_conn.close()
new_conn.close()