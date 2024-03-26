import socket
import ssl
import threading
import time
import logging
from collections import Counter
import bcrypt
from TestDatabase import result_device, device_data
import re
from bson import ObjectId

# SSL context setup
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='TLS/server.crt', keyfile='TLS/server.key')

HOST = '127.0.0.1'
PORT = 65432

clients = {}  # Track clients with their usernames as keys
users = {}  # Track users and their group memberships
groups = {"general": {"members": [], "admin": ""}}  # Track group members and the admin
message_id_counter = 1
error_counts = Counter()
alert_thresholds = {
    'high_connection_count': 10,
    'high_error_rate': 5,  # Per minute
    'high_message_rate': 50,  # Per minute
}
message_rate = 0


# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def alert_system(alert_message):
    print(f"ALERT: {alert_message}")


def monitor_system():
    global message_rate
    while True:
        if len(clients) > alert_thresholds['high_connection_count']:
            alert_system("High number of connections detected.")

        if error_counts['minute'] > alert_thresholds['high_error_rate']:
            alert_system("High error rate detected.")

        if message_rate > alert_thresholds['high_message_rate']:
            alert_system("Unusually high message traffic detected.")

        # Reset counters
        error_counts['minute'] = 0
        message_rate = 0

        time.sleep(60)


def register_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        result_device({"Sender": username, "password": hashed_password})
        return True
    except Exception as e:  # Catch exceptions related to duplicate username or other insertion errors
        print(e)
        return False


def login_user(username, password):
    user = device_data.find_one({"Sender": username})

    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return True
    return False


def send_group_message(group_name, username, message):
    group = groups_collection.find_one({"name": group_name})
    if not group:
        return False, "Group not found."

    # Create a list of current group members' usernames
    visible_to = [member['username'] for member in group['members']]

    messages_collection.insert_one({
        "group_name": group_name,
        "username": username,
        "message": message,
        "timestamp": datetime.datetime.utcnow(),
        "visible_to": visible_to
    })
    return True, "Message sent."


def get_group_messages(group_name, username):
    # Check if user is a member of the group
    if not groups_collection.find_one({"name": group_name, "members.username": username}):
        return False, "You must be a member of the group to view messages."
    # Retrieve messages for the group that are visible to the requesting user
    messages = messages_collection.find({
        "group_name": group_name,
        "visible_to": username
    }).sort("timestamp", -1)
    return True, list(messages)


def delete_message(message_id, username):
    # Attempt to find the message by ID
    message = messages_collection.find_one({"_id": ObjectId(message_id)})

    if not message:
        return False, "Message not found."

    # Check if the user is the sender or an administrator of the group
    group = groups_collection.find_one({
        "name": message["group_name"],
        "$or": [
            {"members": {"$elemMatch": {"username": username, "role": "administrator"}}},
            {"members.username": username, "members": {"$elemMatch": {"username": message["username"]}}}
        ]
    })

    if not group:
        return False, "You don't have permission to delete this message."

    # Update the message to mark it as deleted (or you could actually remove it)
    result = messages_collection.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {"deleted": True}}
    )

    if result.modified_count:
        return True, "Message deleted successfully."
    else:
        return False, "Failed to delete message."


def is_valid_object_id(id):
    return ObjectId.is_valid(id) and re.match(r"^[a-f\d]{24}$", id) is not None


def update_message_visibility(message_id, admin_username, visible_to):
    if not is_valid_object_id(message_id):
        return False, "Invalid message ID format."

        # Sanitize usernames to ensure they match expected patterns
    sanitized_usernames = [username for username in visible_to if re.match(r"^\w+$", username)]
    if len(sanitized_usernames) != len(visible_to):
        return False, "One or more usernames are invalid."

    try:
        # Check if the user is an administrator of any group
        admin_groups = groups_collection.find(
            {"members": {"$elemMatch": {"username": admin_username, "role": "administrator"}}})
        admin_groups = list(admin_groups)  # Convert cursor to list
        if not admin_groups:
            return False, "Permission denied: You're not an administrator."

        # Check for valid message ID
        message = messages_collection.find_one({"_id": ObjectId(message_id)})
        if not message:
            return False, "Invalid message ID."

        # Verify the message belongs to a group the admin manages
        if not any(group["name"] == message["group_name"] for group in admin_groups):
            return False, "Permission denied: Not an admin of the relevant group."

        # Validate user list
        all_usernames = [user['username'] for group in admin_groups for user in group['members']]
        invalid_users = [user for user in visible_to if user not in all_usernames]
        if invalid_users:
            return False, f"Invalid usernames: {', '.join(invalid_users)}"

        # Update message visibility
        result = messages_collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"visible_to": visible_to}}
        )
        if result.modified_count:
            return True, "Message visibility updated successfully."
        else:
            return False, "Failed to update message visibility."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


def handle_client(conn, addr):
    print(f'Connected by {addr}')
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            # Splitting the command and parameters
            command, *params = data.split()

            if command == "send_group_message":
                group_name, message = params[0], " ".join(params[1:])
                success, response = send_group_message(group_name, username, message)
                conn.sendall(response.encode())

            elif command == "delete_message":
                message_id = params[0]
                success, response = delete_message(message_id, username)
                conn.sendall(response.encode())

            elif command.startswith("register"):
                _, username, password = command.split()
                success = register_user(username, password)
                conn.sendall("Registration successful".encode() if success else "Username taken".encode())

            elif command.startswith("login"):
                _, username, password = command.split()
                if login_user(username, password):
                    conn.sendall("Login successful".encode())
                    data = conn.recv(1024)
                    print(f"Received from {addr}: {data.decode()}")
                    conn.sendall(data)  # Echo back the received data
                else:
                    conn.sendall("Login failed".encode())
                    conn.close()
                    return

            elif command == "update_visibility":
                if not username:
                    conn.sendall("Please login first.".encode())
                    continue
                message_id, users_list_str = params[0].split(maxsplit=1)
                visible_to = users_list_str.split(',')
                success, response = update_message_visibility(message_id, username, visible_to)
                conn.sendall(response.encode())
    finally:
        conn.close()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        print(f'Server listening on {HOST}:{PORT}')
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr))
                t.start()

if __name__ == '__main__':
    start_server()
