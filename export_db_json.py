# Exports the newly created ClientConnectionHistory, IPAddresses, AuditLog, ClientConnectionHistory, ClientMessages, Clients, Maps, Metadata, Penalties, PenaltyIdentifiers, Servers & InboxMessages Tables to separate files in .json format.

# Created by Ahrimdon aided by GPT-4

import sqlite3
import json

new_conn = sqlite3.connect("Plutonium_Servers.db")
new_cur = new_conn.cursor()

# ------------------- IPAddresses Table -------------------

new_cur.execute("""
SELECT Name, SearchableIPAddress, DateAdded FROM "IPAddresses"
ORDER BY DateAdded DESC
""")
client_info = new_cur.fetchall()

client_info_list = []
for row in client_info:
    client_info_list.append({
        "Name": row[0],
        "SearchableIPAddress": row[1],
        "DateAdded": row[2]
    })

with open("IPAddresses.json", "w") as f:
    json.dump(client_info_list, f, indent=2)

# ------------------- AuditLog Table -------------------

new_cur.execute("""
SELECT ChangeHistoryId, TypeOfChange, Time, Data, Command, Origin, Target FROM AuditLog
ORDER BY Time DESC
""")
ef_change_history = new_cur.fetchall()

ef_change_history_list = []
for row in ef_change_history:
    ef_change_history_list.append({
        "ChangeHistoryId": row[0],
        "TypeOfChange": row[1],
        "Time": row[2],
        "Data": row[3],
        "Command": row[4],
        "Origin": row[5],
        "Target": row[6]
    })

with open("AuditLog.json", "w") as f:
    json.dump(ef_change_history_list, f, indent=2)

# ------------------- ClientConnectionHistory Table -------------------

new_cur.execute("""
SELECT ConnectionId, Client, ConnectionTime, ConnectionType, Server
FROM ClientConnectionHistory
ORDER BY ConnectionTime DESC
""")
client_connection_history = new_cur.fetchall()

client_connection_history_list = []
for row in client_connection_history:
    client_connection_history_list.append({
        "ConnectionId": row[0],
        "Client": row[1],
        "ConnectionTime": row[2],
        "ConnectionType": row[3],
        "Server": row[4]
    })

with open("ClientConnectionHistory.json", "w") as f:
    json.dump(client_connection_history_list, f, indent=2)

# ------------------- Messages Table -------------------

new_cur.execute("""
SELECT MessageId, Client, Message, TimeSent, Server
FROM ClientMessages
ORDER BY TimeSent DESC
""")
client_messages = new_cur.fetchall()

client_messages_list = []
for row in client_messages:
    client_messages_list.append({
        "MessageId": row[0],
        "Client": row[1],
        "Message": row[2],
        "TimeSent": row[3],
        "Server": row[4]
    })

with open("ClientMessages.json", "w") as f:
    json.dump(client_messages_list, f, indent=2)

# ------------------- Clients Table -------------------

new_cur.execute("""
SELECT Connections, Name, FirstConnection, Game, LastConnection, Level, Masked, TotalConnectionTime
FROM Clients
ORDER BY LastConnection DESC
""")
clients = new_cur.fetchall()

clients_list = []
for row in clients:
    clients_list.append({
        "Connections": row[0],
        "Name": row[1],
        "FirstConnection": row[2],
        "Game": row[3],
        "LastConnection": row[4],
        "Level": row[5],
        "Masked": row[6],
        "TotalConnectionTime": row[7]
    })

with open("Clients.json", "w") as f:
    json.dump(clients_list, f, indent=2)

# ------------------- Maps Table -------------------

new_cur.execute("""
SELECT
    MapId, CreatedDateTime, Name, Game
FROM
    Maps
ORDER BY
    MapId DESC
""")
rows = new_cur.fetchall()

maps_list = []
for row in rows:
    map_dict = {
        "MapId": row[0],
        "CreatedDateTime": row[1],
        "Name": row[2],
        "Game": row[3]
    }
    maps_list.append(map_dict)

with open("maps_export.json", "w") as json_file:
    json.dump(maps_list, json_file, indent=4)

# ------------------- Meta Table -------------------

new_cur.execute("""
SELECT MetaId, Name, Timestamp, Note, Value
FROM Metadata
ORDER BY Timestamp DESC
""")
metadata = new_cur.fetchall()

metadata_list = []
for row in metadata:
    metadata_list.append({
        "MetaId": row[0],
        "Name": row[1],
        "Timestamp": row[2],
        "Note": row[3],
        "Value": row[4]
    })

with open("Metadata.json", "w") as f:
    json.dump(metadata_list, f, indent=2)

# ------------------- Penalties Table -------------------

new_cur.execute("""
SELECT PenaltyId, AutomatedOffense, Expires, EvadedOffense, Offender, Offense, Punisher, Type, Timestamp
FROM Penalties
ORDER BY Timestamp DESC
""")
penalties = new_cur.fetchall()

penalties_list = []
for row in penalties:
    penalties_list.append({
        "PenaltyId": row[0],
        "AutomatedOffense": row[1],
        "Expires": row[2],
        "EvadedOffense": row[3],
        "Offender": row[4],
        "Offense": row[5],
        "Punisher": row[6],
        "Type": row[7],
        "Timestamp": row[8]
    })

with open("Penalties.json", "w") as f:
    json.dump(penalties_list, f, indent=2)

# ------------------- PenaltyIdentifiers Table -------------------

new_cur.execute("""
SELECT PenaltyIdentifierId, PenaltyId, Created, Client
FROM PenaltyIdentifiers
ORDER BY Created DESC
""")
penalty_identifiers = new_cur.fetchall()

penalty_identifiers_list = []
for row in penalty_identifiers:
    penalty_identifiers_list.append({
        "PenaltyIdentifierId": row[0],
        "PenaltyId": row[1],
        "Created": row[2],
        "Client": row[3]
    })

with open("PenaltyIdentifiers.json", "w") as f:
    json.dump(penalty_identifiers_list, f, indent=2)

# ------------------- Servers Table -------------------

new_cur.execute("""
SELECT ServerId, Active, Port, Endpoint, Game, ServerName, Password
FROM Servers
""")
servers = new_cur.fetchall()

servers_list = []
for row in servers:
    servers_list.append({
        "ServerId": row[0],
        "Active": row[1],
        "Port": row[2],
        "Endpoint": row[3],
        "Game": row[4],
        "ServerName": row[5],
        "Password": row[6]
    })

with open("Servers.json", "w") as f:
    json.dump(servers_list, f, indent=2)

# ------------------- InboxMessages Table -------------------

new_cur.execute("""
SELECT InboxMessageId, Created, Origin, Target, ServerId, Message, Read
FROM InboxMessagesModified
ORDER BY Created DESC
""")
inbox_messages = new_cur.fetchall()

inbox_messages_list = []
for row in inbox_messages:
    inbox_messages_list.append({
        "InboxMessageId": row[0],
        "Created": row[1],
        "Origin": row[2],
        "Target": row[3],
        "ServerId": row[4],
        "Message": row[5],
        "Read": row[6]
    })

with open("InboxMessages.json", "w") as f:
    json.dump(inbox_messages_list, f, indent=2)

# ------------------- End -------------------

new_conn.close()