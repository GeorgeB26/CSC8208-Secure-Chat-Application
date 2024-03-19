import socket
import threading
import bcrypt
import time
from collections import Counter
import ssl
import logging

HOST = '127.0.0.1'
PORT = 65432

# SSL context setup
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='certificate.pem', keyfile='key.pem')

clients = []
users = {}
groups = {"general": []}
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


def client_thread(conn, addr):
    global message_id_counter
    is_authenticated = False
    current_group = "general"
    username = ""

    try:
        while not is_authenticated:
            auth_data = conn.recv(1024).decode()
            username, password, mode = auth_data.split(':')

            if mode == 'register':
                if username in users:
                    conn.send("Username already taken. Try a different one.".encode())
                else:
                    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    users[username] = hashed
                    conn.send("Registration successful. You can now login.".encode())
            elif mode == 'login':
                if username in users and bcrypt.checkpw(password.encode(), users[username]):
                    conn.send("Login successful. Welcome to the general group!".encode())
                    is_authenticated = True
                    groups[current_group].append(conn)
                else:
                    conn.send("Invalid login. Try again.".encode())

        while True:
            data = conn.recv(1024).decode()
            if data.startswith('delete:'):
                _, msg_id_str = data.split(':')
                broadcast(f"delete:{msg_id_str}", current_group, include_self=True)
            elif data.startswith('join:'):
                _, group_name = data.split(':')
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(conn)
                if conn in groups[current_group]:
                    groups[current_group].remove(conn)
                current_group = group_name
                conn.send(f"You have joined {group_name} group.".encode())
            elif data:
                broadcast(f"{username} says: {data}", current_group)
            else:
                remove(conn, current_group)
                break
    except Exception as e:
        logging.error(f"Error with client {addr}: {e}")
        remove(conn, current_group)


def broadcast(message, group_name, include_self=False):
    for client in groups[group_name]:
        try:
            client.send(message.encode())
        except Exception as e:
            logging.error(f"Broadcast error: {e}")
            remove(client, group_name)


def remove(connection, group_name):
    if connection in groups[group_name]:
        groups[group_name].remove(connection)
        logging.info(f"Removed connection from {group_name}. Total connections: {len(clients)}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Secure server started, listening on {HOST}:{PORT}...')

        while True:
            client_socket, addr = server_socket.accept()
            secure_conn = context.wrap_socket(client_socket, server_side=True)

            print(f'Secure connection established with {addr}')
            t = threading.Thread(target=client_thread, args=(secure_conn, addr))
            t.start()


start_server()
