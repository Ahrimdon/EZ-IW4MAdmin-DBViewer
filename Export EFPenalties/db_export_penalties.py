import sqlite3
import re

# Connect to the existing database
existing_conn = sqlite3.connect("Database.db")
existing_cur = existing_conn.cursor()

# Connect to the new database
new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# Create the modified Penalties table in the new database
new_cur.execute("""
CREATE TABLE "Penalties" (
    "PenaltyId" INTEGER NOT NULL,
    "AutomatedOffense" TEXT NOT NULL,
    "Expires" INTEGER,  -- This line is modified to allow NULL values
    "EvadedOffense" TEXT NOT NULL,
    "Offender" TEXT NOT NULL,
    "Offense" TEXT NOT NULL,
    "Punisher" TEXT NOT NULL,
    "Type" TEXT NOT NULL,
    "Timestamp" INTEGER NOT NULL
)
""")

# Fetch data from existing EFPenalties
existing_cur.execute("""
SELECT
    EFPenalties.PenaltyId,
    EFPenalties.AutomatedOffense,
    EFPenalties.Expires,
    EFPenalties.IsEvadedOffense,
    EFPenalties.OffenderId,
    EFPenalties.Offense,
    EFPenalties.PunisherId,
    EFPenalties.Type,
    EFPenalties."When"
FROM
    EFPenalties
""")
rows = existing_cur.fetchall()

for row in rows:
    penalty_id = row[0]
    automated_offense = row[1]
    expires = row[2]
    evaded_offense = row[3]
    offender_id = row[4]
    offense = row[5]
    punisher_id = row[6]
    penalty_type = row[7]
    timestamp = row[8]

    # Retrieve offender name
    existing_cur.execute("""
    SELECT
        EFAlias.Name
    FROM
        EFAlias
    INNER JOIN
        EFClients ON EFAlias.AliasId = EFClients.CurrentAliasId
    WHERE
        EFClients.ClientId = ?
    """, (offender_id,))
    offender_name = existing_cur.fetchone()
    if offender_name:
        offender_name = offender_name[0].replace('^7', '')
    else:
        offender_name = 'Unknown'

    # Retrieve punisher name
    existing_cur.execute("""
    SELECT
        EFAlias.Name
    FROM
        EFAlias
    INNER JOIN
        EFClients ON EFAlias.AliasId = EFClients.CurrentAliasId
    WHERE
        EFClients.ClientId = ?
    """, (punisher_id,))
    punisher_name = existing_cur.fetchone()
    if punisher_name:
        punisher_name = punisher_name[0].replace('^7', '')
    else:
        punisher_name = 'Unknown'

    # Replace Type values
    type_map = {0: "Report", 1: "Warning", 2: "Flag", 3: "Kick", 4: "Temp Ban", 5: "Perm Ban", 6: "Unban", 8: "Unflag"}
    penalty_type = type_map.get(penalty_type, f"Unknown Type ({penalty_type})")

    # Set AutomatedOffense value to 'Yes' or 'No'
    automated_offense_patterns = [r"VPNs are not allowed",
                                  r"Ping is too high!",
                                  r"name is not allowed"]  # Simplified the patterns

    # Search the 'Offense' field for specified patterns
    for pattern in automated_offense_patterns:
        if re.search(pattern, offense):  # Using re.search with 'offense' instead of 'automated_offense'
            automated_offense = "Yes"
            break
    else:
        automated_offense = "No"

    # Set EvadedOffense values to 'Yes' or 'No'
    evaded_offense = "Yes" if evaded_offense == 1 else "No"

    # Set Expires value to 'Never' if it is NULL
    expires = "Never" if expires is None else expires

    # Insert the modified row into the new Penalties table
    new_cur.execute("""
    INSERT INTO Penalties (
        PenaltyId,
        AutomatedOffense,
        Expires,
        EvadedOffense,
        Offender,
        Offense,
        Punisher,
        Type,
        Timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (penalty_id, automated_offense, expires, evaded_offense, offender_name, offense, punisher_name, penalty_type, timestamp))

# Commit changes and close the new database
new_conn.commit()
new_conn.close()

# Close the existing database
existing_conn.close()