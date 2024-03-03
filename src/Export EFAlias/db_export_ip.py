import sqlite3

# Connect to the existing database
conn = sqlite3.connect("Database.db")
cur = conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

def fetch_client_info(src_cur):
    src_cur.execute("""
    SELECT Name, SearchableIPAddress, DateAdded FROM EFAlias
    """)
    client_info = []
    for row in src_cur.fetchall():
        name = row[0].replace('^7', '')  # Remove '^7' from the Name column
        client_info.append((name, row[1], row[2]))

    return client_info

# Fetch client info from EFAlias table in the existing database
client_info = fetch_client_info(cur)

# Create the new table
new_cur.execute("""
CREATE TABLE IF NOT EXISTS "IPAddresses" (
    Name TEXT NOT NULL,
    SearchableIPAddress TEXT,
    DateAdded TEXT NOT NULL
)
""")

# Insert the fetched data into the new table
new_cur.executemany("""
INSERT INTO "IPAddresses" (
    Name, SearchableIPAddress, DateAdded
) VALUES (?, ?, ?)
""", client_info)

# Commit and close the new database
new_conn.commit()
new_conn.close()

# Close the existing database
conn.close()