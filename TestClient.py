import socket
import threading
import ssl

HOST = '127.0.0.1'
PORT = 65432

# SSL context setup
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations('certificate.pem')


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


def start_client():
    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as secure_sock:
            print(f'Secure connection established with {HOST}:{PORT}')

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
            elif message.startswith('delete '):
                msg_id = message.split(' ')[1]
                secure_sock.send(f"delete:{msg_id}".encode())
            elif message.startswith('join '):
                group_name = message.split(' ')[1]
                secure_sock.send(f"join:{group_name}".encode())
            elif message:
                secure_sock.send(message.encode())


start_client()
