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

print("Successful")

for doc in collection.find():
    print(doc)

# Data
device_data = {
    "Device_id": 1,
    "Sender": "Sender's Name or ID",
    "GroupID": "Group's Identifier",
    "Data": "Some data or message",
    "Timestamp": datetime.now()
}

server_data = {
    "Server_id": 1,
    "Device_id": device_data['Device_id'],
    "EncryptedData": "some_encrypted_data",
    "Timestamp": datetime.now()
}

backup_data ={
    "Backup_id": 1,
    "Server_id": server_data['Server_id'],
    "Device_id": device_data['Device_id'],
    "EncryptedData": server_data['EncryptedData'],
    "Timestamp": datetime.now(),
    "Status": "status of backup"
}

chat_session_document = {
    "Device_id": device_data['Device_id'],
    "StartTime": datetime.now(),
    "EndTime": datetime.now() + timedelta(hours=1)  # Assume the time delta is an hour
}

biometrics_data = {
    "biometrics_id": 1,
    "Device_id": device_data['Device_id'],
    "Data": "Biometrics data"
}

group_data = {
    "Group_id": 1,
    "GroupName": "Group name",
    "Creator_id": "Creator's id",
    "Timestamp": datetime.now()
}

group_members_data = {
    "Group_id": group_data['Group_id'],
    "member_id": "Group members' id",
    "Timestamp": datetime.now()
}


# insert the data to collections
result_device = db.Devices.insert_one(device_data)
result_server = db.Servers.insert_one(server_data)
result_backup = db.Backup.insert_one(backup_data)
result_chat_session_document = db.ChatSession.insert_one(chat_session_document)
result_biometrics = db.Biometrics.insert_one(biometrics_data)
result_group = db.Group.insert_one(group_data)
result_group_members = db.GroupMembers.insert_one(group_members_data)

print(f"Inserted document with id {result_device.inserted_id}")
print(f"Inserted document with id {result_server.inserted_id}")
print(f"Inserted document with id {result_backup.inserted_id}")
print(f"Inserted document with id {result_chat_session_document.inserted_id}")
print(f"Inserted document with id {result_biometrics.inserted_id}")
print(f"Inserted document with id {result_group.inserted_id}")
print(f"Inserted document with id {result_group_members.inserted_id}")
