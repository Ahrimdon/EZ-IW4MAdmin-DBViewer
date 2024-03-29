'''
Title: parse_db.py
Created by: Ahrimdon (aided by GPT-4)

Description: This script parses key elements of IW4MAdmin's database into a single consolidated, easy to read database that allows for easy server administration and logging.
'''

import sqlite3
import argparse
import time
import json
import os
import re

def setup_argparser():
    parser = argparse.ArgumentParser(description="Accurately parses IW4MAdmin's database into a consolidated, easy-to-read format.")
    parser.add_argument('-s', '--sort', type=str, choices=['ASC', 'DESC'], default='DESC', help="Sort order for the query results (ASC or DESC).")
    parser.add_argument('-p', '--path', type=str, default="Database.db", help="Path to the IW4MAdmin database file.")
    parser.add_argument('-o', '--output', type=str, help="Output directory for the parsed database file.")
    parser.add_argument('-t', '--time', action='store_true', help="Time the script's execution.")
    parser.add_argument('-c', '--config', action='store_true', help="Use default config.json for configuration.")
    return parser.parse_args()

def delete_existing_db(output_db_path):
    """Check for an existing parsed DB and delete it if found."""
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
        print(f"Existing parsed database at {output_db_path} has been removed.")

def load_or_create_config():
    config_path = "config.json"  # Always use config.json
    default_config = {
        "tables": {
            "AuditLog": 1000,
            "ClientConnectionHistory": 1000,
            "ClientMessages": 1000,
            "Clients": 1000,
            "IPAddresses": 1000,
            "InboxMessagesModified": 1000,
            "Maps": 1000,
            "Metadata": 1000,
            "Penalties": 1000,
            "PenaltyIdentifiers": 1000,
            "Servers": 1000,
        }
    }
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        print(f"Default configuration file created at {config_path}")
    else:
        with open(config_path) as config_file:
            return json.load(config_file)
    return default_config

def main():
    args = setup_argparser()

    if args.time:
        total_start_time = time.time()  # Start timing for the entire script

    config = {}
    if args.config:
        config = load_or_create_config()

    db_path = args.path
    output_dir = args.output if args.output else '.'  # Use current directory if no output directory is specified
    output_db_path = os.path.join(output_dir, "Database_parsed.db")

    # Ensure the output directory exists
    if not os.path.isdir(output_dir):
        print(f"Creating output directory at {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    # Delete existing parsed database if it exists
    delete_existing_db(output_db_path)

    # Check if the specified Database.db exists
    if not os.path.isfile(db_path):
        print(f"No database file ({db_path}) found. Please ensure the file exists.")
        return  # Exit the script if file not found

    existing_conn = sqlite3.connect(db_path)
    existing_cur = existing_conn.cursor()

    new_conn = sqlite3.connect(output_db_path)
    new_cur = new_conn.cursor()

    # Define a mapping of table names to their processing functions
    table_functions = {
        'AuditLog': audit_log_table,
        'ClientConnectionHistory': client_connection_history_table,
        'ClientMessages': client_messages_table,
        'Clients': clients_table,
        'IPAddresses': ip_address_table,
        'InboxMessagesModified': inbox_messages_modified_table,
        'Maps': maps_table,
        'Metadata': metadata_table,
        'Penalties': penalties_table,
        'PenaltyIdentifiers': penalty_identifiers_table,
        'Servers': servers_table,
    }

    sort_order = args.sort

    if args.time:
        sqlite_start_time = time.time()  # Start timing for SQLite operations

    # Process each table according to the configuration
    for table_name, func in table_functions.items():
        limit = config.get('tables', {}).get(table_name)
        if limit is not None:
            print(f"Processing {table_name} with limit: {limit}")
            func(existing_cur, new_cur, limit=limit, sort_order=sort_order)  # Assuming each function can accept a limit parameter
        else:
            print(f"Processing {table_name} without limit")
            func(existing_cur, new_cur, sort_order=sort_order)

    # Commit and close
    new_conn.commit() # Commit changes before vacuuming
    if args.time:
        sqlite_end_time = time.time()  # End timing for SQLite operations
        print(f"SQLite execution time: {sqlite_end_time - sqlite_start_time:.4f} seconds")

    # Vacuum process timing
    if args.time:
        vacuum_start_time = time.time()  # Start timing for vacuuming

    new_conn.execute("VACUUM;")
    new_conn.commit()

    if args.time:
        vacuum_end_time = time.time()  # End timing for vacuuming
        print(f"Vacuuming duration: {vacuum_end_time - vacuum_start_time:.4f} seconds")
    
    existing_conn.close()
    new_conn.close()

    if args.time:
        total_end_time = time.time()  # End timing for the entire script
        print(f"Total script execution time: {total_end_time - total_start_time:.4f} seconds")

def audit_log_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
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
    ORDER BY ChangeHistoryId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    rows = existing_cur.fetchall()

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

        type_of_change_map = {0: "Console", 1: "Punishment", 2: "Client"}
        type_of_change = type_of_change_map[row[1]]

        new_row = (row[0], type_of_change, row[2], row[3], row[4], client_name_map[origin_entity_id], client_name_map[target_entity_id])
        new_cur.execute("INSERT INTO \"AuditLog\" (ChangeHistoryId, TypeOfChange, Time, Data, Command, Origin, Target) VALUES (?, ?, ?, ?, ?, ?, ?)", new_row)

def client_connection_history_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
    SELECT
        EFClientConnectionHistory.ClientConnectionId,
        EFClientConnectionHistory.ClientId,
        EFClientConnectionHistory.CreatedDateTime,
        EFClientConnectionHistory.ConnectionType,
        EFClientConnectionHistory.ServerId
    FROM
        EFClientConnectionHistory
    ORDER BY ClientConnectionId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    rows = existing_cur.fetchall()

    for row in rows:
        client_id = row[1]
        server_id = row[4]
        
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

        connection_type_map = {0: "Connect", 1: "Disconnect"}
        connection_type = connection_type_map[row[3]]
        
        new_row = (row[0], client_name, row[2], connection_type, server_hostname)
        new_cur.execute("INSERT INTO ClientConnectionHistory (ConnectionId, Client, ConnectionTime, ConnectionType, Server) VALUES (?, ?, ?, ?, ?)", new_row)

def client_messages_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
    SELECT
        EFClientMessages.MessageId,
        EFClientMessages.ClientId,
        EFClientMessages.Message,
        EFClientMessages.TimeSent,
        EFClientMessages.ServerId
    FROM
        EFClientMessages
    ORDER BY MessageId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    rows = existing_cur.fetchall()

    for row in rows:
        client_id = row[1]
        server_id = row[4]

        
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

        
        new_row = (row[0], client_name, row[2], row[3], server_hostname)
        new_cur.execute("INSERT INTO ClientMessages (MessageId, Client, Message, TimeSent, Server) VALUES (?, ?, ?, ?, ?)", new_row)

def clients_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
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
    ORDER BY LastConnection {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
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

        
        level_map = {-1: "Banned", 0: "User", 1: "Trusted", 2: "Moderator", 3: "Administrator", 4: "Senior Administrator", 5: "Owner", 6: "Creator", 7: "Console"}
        level = level_map.get(level, f"Unknown Level ({level})")

        
        game_map = {5: "WaW", 6: "BO", 7: "BO2", 3: "MW3"}
        game = game_map.get(game_name, f"Unknown Game ({game_name})")

        
        new_row = (connections, client_name, first_connection, game, last_connection, level, masked, total_connection_time, ip_address)
        new_cur.execute("INSERT INTO Clients (Connections, Name, FirstConnection, Game, LastConnection, Level, Masked, TotalConnectionTime, IP) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", new_row)

def ip_address_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
    query = f"""
    SELECT Name, SearchableIPAddress, DateAdded
    FROM EFAlias
    ORDER BY DateAdded {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    client_info = [(row[0].replace('^7', ''), row[1], row[2]) for row in existing_cur.fetchall()]

    new_cur.execute("""
    CREATE TABLE IF NOT EXISTS "IPAddresses" (
        Name TEXT NOT NULL,
        SearchableIPAddress TEXT,
        DateAdded TEXT NOT NULL
    )
    """)

    new_cur.executemany("""
    INSERT INTO "IPAddresses" (
        Name, SearchableIPAddress, DateAdded
    ) VALUES (?, ?, ?)
    """, client_info)

def inbox_messages_modified_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
    SELECT InboxMessageId, CreatedDateTime, SourceClientId, DestinationClientId, ServerId, Message, IsDelivered
    FROM InboxMessages
    ORDER BY InboxMessageId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    inbox_messages = existing_cur.fetchall()

    for msg in inbox_messages:
        msg_id, created, source_client_id, dest_client_id, server_id, message, is_delivered = msg

        origin = fetch_client_name(existing_cur, source_client_id)
        target = fetch_client_name(existing_cur, dest_client_id)
        read = "Yes" if is_delivered == 1 else "No"

        new_cur.execute("""
        INSERT INTO InboxMessagesModified (InboxMessageId, Created, Origin, Target, ServerId, Message, Read)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, created, origin, target, server_id, message, read))

def fetch_client_name(cur, client_id):
    cur.execute("SELECT CurrentAliasId FROM EFClients WHERE ClientId = ?", (client_id,))
    alias_id = cur.fetchone()
    if alias_id:
        alias_id = alias_id[0]
        cur.execute("SELECT Name FROM EFAlias WHERE AliasId = ?", (alias_id,))
        name = cur.fetchone()
        if name:
            return name[0].replace('^7', '')
    return 'Unknown'

def maps_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
    new_cur.execute("""
    CREATE TABLE IF NOT EXISTS "Maps" (
        "MapId" INTEGER NOT NULL,
        "CreatedDateTime" TEXT NOT NULL,
        "Name" TEXT NOT NULL,
        "Game" TEXT NOT NULL,
        CONSTRAINT "PK_Maps" PRIMARY KEY("MapId" AUTOINCREMENT)
    )
    """)

    query = f"""
    SELECT
        MapId, CreatedDateTime, Name, Game
    FROM
        EFMaps
    ORDER BY MapId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    rows = existing_cur.fetchall()

    modified_rows = []
    for row in rows:
        game_map = {5: "WaW", 6: "BO", 7: "BO2", 3: "MW3"}
        game = game_map.get(row[3], f"Unknown Game ({row[3]})")
        modified_rows.append((row[0], row[1], row[2], game))

    new_cur.executemany("""
    INSERT INTO "Maps" (
        MapId, CreatedDateTime, Name, Game
    ) VALUES (?, ?, ?, ?)
    """, modified_rows)

def metadata_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
    new_cur.execute("""
    CREATE TABLE "Metadata" (
        "MetaId" INTEGER NOT NULL,
        "Name" TEXT NOT NULL,
        "Timestamp" TEXT NOT NULL,
        "Note" TEXT NOT NULL,
        "Value" TEXT NOT NULL
    )
    """)

    query = f"""
    SELECT
        EFMeta.MetaId,
        EFMeta.ClientId,
        EFMeta.Created,
        EFMeta.Key,
        EFMeta.Value
    FROM
        EFMeta
    ORDER BY MetaId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    rows = existing_cur.fetchall()

    for row in rows:
        meta_id = row[0]
        client_id = row[1]
        created = row[2]
        key = row[3]
        value = row[4]

        
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

        
        new_row = (meta_id, client_name, created, key, value)
        new_cur.execute("INSERT INTO Metadata (MetaId, Name, Timestamp, Note, Value) VALUES (?, ?, ?, ?, ?)", new_row)

def penalties_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
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
    ORDER BY PenaltyId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
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

        
        type_map = {0: "Report", 1: "Warning", 2: "Flag", 3: "Kick", 4: "Temp Ban", 5: "Perm Ban", 6: "Unban", 8: "Unflag"}
        penalty_type = type_map.get(penalty_type, f"Unknown Type ({penalty_type})")

        
        automated_offense_patterns = [r"VPNs are not allowed",
                                    r"Ping is too high!",
                                    r"name is not allowed"]  

        
        for pattern in automated_offense_patterns:
            if re.search(pattern, offense):  
                automated_offense = "Yes"
                break
        else:
            automated_offense = "No"

        
        evaded_offense = "Yes" if evaded_offense == 1 else "No"

        
        expires = "Never" if expires is None else expires

        
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

def penalty_identifiers_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
    new_cur.execute("""
    CREATE TABLE "PenaltyIdentifiers" (
        "PenaltyIdentifierId" INTEGER NOT NULL,
        "PenaltyId" INTEGER NOT NULL,
        "Created" TEXT NOT NULL,
        "Client" TEXT NOT NULL
    )
    """)

    query = f"""
    SELECT
        EFPenaltyIdentifiers.PenaltyIdentifierId,
        EFPenaltyIdentifiers.PenaltyId,
        EFPenaltyIdentifiers.CreatedDateTime,
        EFPenaltyIdentifiers.NetworkId
    FROM
        EFPenaltyIdentifiers
    ORDER BY PenaltyIdentifierId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
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

def servers_table(existing_cur, new_cur, limit=None, sort_order='DESC'):
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

    query = f"""
    SELECT ServerId, Active, Port, Endpoint, GameName, HostName, IsPasswordProtected
    FROM EFServers
    ORDER BY ServerId {sort_order}
    """
    if limit:
        query += f" LIMIT {limit}"

    existing_cur.execute(query)
    rows = existing_cur.fetchall()

    game_mapping = {5: "WaW", 7: "BO2", 6: "BO", 3: "MW3"}

    for row in rows:
        server_id = row[0]
        active = row[1]
        port = row[2]
        endpoint = row[3]
        game_name = row[4]
        server_name = row[5]
        is_password_protected = row[6]

        game_name = game_mapping.get(game_name, game_name)

        password = "Yes" if is_password_protected == 1 else "No"

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

if __name__ == '__main__':
    main()