import socket
import threading
import ssl

HOST = '127.0.0.1'
PRIMARY_PORT = 65432
BACKUP_PORT = 65433

# SSL context setup
# context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
# context.load_verify_locations('certificate.pem')
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


def receive_message(s):
    while True:
        try:
            message = s.recv(1024).decode()
            if message.startswith('delete:'):
                msg_id = message.split(':')[1]
                print(f"Message {msg_id} has been deleted.")
            else:
                print(message)
        except:
            print("You have been disconnected from the server.")
            s.close()
            break


def connect_to_server(host, port):
    try:
        sock = socket.create_connection((host, port))
        secure_sock = context.wrap_socket(sock, server_hostname=host)
        print(f'Secure connection established with {host}:{port}')
        return secure_sock
    except (ConnectionRefusedError, TimeoutError):
        print(f'Failed to connect to {host}:{port}')
        return None


def start_client():
    secure_sock = connect_to_server(HOST, PRIMARY_PORT)

    # Fallback to backup server if primary connection fails
    if not secure_sock:
        print('Trying to connect to the backup server...')
        secure_sock = connect_to_server(HOST, BACKUP_PORT)

    if not secure_sock:
        print('Could not connect to any server.')
        return

    while True:
        mode = input("Choose 'register' or 'login': ")
        if mode in ['register', 'login']:
            username = input("Username: ")
            password = input("Password: ")
            auth_data = f"{username}:{password}:{mode}"
            secure_sock.send(auth_data.encode())
            response = secure_sock.recv(1024).decode()
            print(response)
            if "successful" in response:
                break

        threading.Thread(target=receive_message, args=(secure_sock,)).start()

        while True:
            message = input('')
            if message.lower() == 'exit':
                break
            elif message.startswith('create_group '):
                group_name = message.split(' ')[1]
                secure_sock.send(f"create_group:{group_name}".encode())
            elif message.startswith('delete '):
                msg_id = message.split(' ')[1]
                secure_sock.send(f"delete:{msg_id}".encode())
            elif message.startswith('join '):
                group_name = message.split(' ')[1]
                secure_sock.send(f"join:{group_name}".encode())
            elif message:
                secure_sock.send(message.encode())


start_client()
