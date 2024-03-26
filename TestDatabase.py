# import mysql.connector
#
# # Connect to DB (Local database)
# conn = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='WC.cw0718',
#     database='csc8208'
# )
#
# cursor = conn.cursor()
#
# # Test
# cursor.execute('SELECT * FROM devicedata')
#
# # Result
# records = cursor.fetchall()
#
# # Print
# for record in records:
#     print(record)
#
# # Close connection
# cursor.close()
# conn.close()

"""
    Details of database:
        Host: localhost
        Port: 27017
        Database: CSC8208
        Username: root
        Password: WC.cw0718
"""
from datetime import datetime, timedelta

from pymongo import MongoClient

# MongoDB Client
client = MongoClient('localhost', 27017)

# Connect to db
db = client['CSC8208']

# Connect to collections
collection = db['Test']
devices_collection = db['devices_collection']

print("Successful")

for doc in collection.find():
    print(doc)

# Data
user_data = {
    "username": "username",
    "password": "password encrypted"
}

device_data = {
    "Sender": "Sender's Name or ID",
    "GroupID": "Group's Identifier",
    "Data": "Some data or message",
    "Timestamp": datetime.now()
}

server_data = {
    "Server_id": 1,
    "EncryptedData": "some_encrypted_data",
    "Timestamp": datetime.now()
}

backup_data = {
    "Backup_id": 1,
    "Server_id": server_data['Server_id'],
    "EncryptedData": server_data['EncryptedData'],
    "Timestamp": datetime.now(),
    "Status": "status of backup"
}

chat_session_document = {
    "StartTime": datetime.now(),
    "EndTime": datetime.now() + timedelta(hours=1)  # Assume the time delta is an hour
}

biometrics_data = {
    "biometrics_id": 1,
    "Data": "Biometrics data"
}

group_data = {
    "name": "Group name",
    "members_username": user_data['username'],
    "role": "role of group members",
    "Timestamp": datetime.now()
}

group_members_data = {
    "member_id": "Group members' id",
    "role": "role of group members",
    "Timestamp": datetime.now()
}

messages_data = {
    "group_name": group_data['name'],
    "username": user_data["username"],
    "message": "message",
    "timestamp": datetime.now(),
    "visible_to": user_data["username"]
}

# insert the data to collections
result_device = db.devices_collection.insert_one(device_data)
result_server = db.Servers.insert_one(server_data)
result_backup = db.Backup.insert_one(backup_data)
result_chat_session_document = db.ChatSession.insert_one(chat_session_document)
result_biometrics = db.Biometrics.insert_one(biometrics_data)
result_group = db.groups_collection.insert_one(group_data)
result_group_members = db.GroupMembers.insert_one(group_members_data)
result_users = db.users_collection.insert_one(user_data)
result_messages = db.messages_collection.insert_one(messages_data)

print(f"Inserted document with id {result_device.inserted_id}")
print(f"Inserted document with id {result_server.inserted_id}")
print(f"Inserted document with id {result_backup.inserted_id}")
print(f"Inserted document with id {result_chat_session_document.inserted_id}")
print(f"Inserted document with id {result_biometrics.inserted_id}")
print(f"Inserted document with id {result_group.inserted_id}")
print(f"Inserted document with id {result_group_members.inserted_id}")
print(f"Inserted document with id {result_messages.inserted_id}")
