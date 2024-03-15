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
        DB: CSC8208
        Username: root
        Password: WC.cw0718
"""

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

