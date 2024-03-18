import socket
import threading
import bcrypt
import logging

HOST = '127.0.0.1'
PORT = 65432

clients = []
users = {}
groups = {"general": []}
message_id_counter = 1

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def monitor_system():
    while True:
        try:
            # Example monitoring: Log the number of active connections every minute
            logging.info(f"Current active connections: {len(clients)}")
            for group, members in groups.items():
                logging.info(f"{group} group has {len(members)} members")
            threading.Event().wait(60)
        except Exception as e:
            logging.error(f"Monitoring error: {e}")


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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f'Server started, listening on {HOST}:{PORT}...')

        # Start system monitoring in a separate thread
        threading.Thread(target=monitor_system, daemon=True).start()

        while True:
            conn, addr = s.accept()
            clients.append(conn)
            logging.info(f"New connection from {addr}. Total connections: {len(clients)}")
            t = threading.Thread(target=client_thread, args=(conn, addr))
            t.start()


start_server()