import socket
import threading

HOST = '127.0.0.1'
PORT = 65432


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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            mode = input("Choose 'register' or 'login': ")
            if mode in ['register', 'login']:
                username = input("Username: ")
                password = input("Password: ")
                auth_data = f"{username}:{password}:{mode}"
                s.send(auth_data.encode())
                response = s.recv(1024).decode()
                print(response)
                if "successful" in response:
                    break

        threading.Thread(target=receive_message, args=(s,)).start()

        while True:
            message = input('')
            if message.lower() == 'exit':
                break
            elif message.startswith('delete '):
                msg_id = message.split(' ')[1]
                s.send(f"delete:{msg_id}".encode())
            elif message.startswith('join '):
                group_name = message.split(' ')[1]
                s.send(f"join:{group_name}".encode())
            elif message:
                s.send(message.encode())


start_client()