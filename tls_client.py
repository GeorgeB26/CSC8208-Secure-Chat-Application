import socket
import ssl

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
BACKUP_PORT = 65433

# SSL context setup
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations('TLS/server.crt')
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED


def start_client():
    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            # Registration or Login
            action = input("Register or Login? (r/l): ")
            if action.lower() == 'r':
                username = input("Username: ")
                password = input("Password: ")
                ssock.sendall(f"register {username} {password}".encode())
            elif action.lower() == 'l':
                username = input("Username: ")
                password = input("Password: ")
                ssock.sendall(f"login {username} {password}".encode())

            response = ssock.recv(1024).decode()
            print(response)
            if "successful" not in response:
                return

            # Proceed to chat functionality if login successful
            print('SSL connection established. Enter "exit" to quit.')
            while True:
                message = input("Message: ")
                if message == "exit":
                    break
                ssock.sendall(message.encode())
                data = ssock.recv(1024)
                print(f"Received: {data.decode()}")

            while True:
                print("Commands: send_group_message, update_visibility, logout")
                command = input("Enter command: ")
                if command == "logout":
                    break
                elif command == "send_group_message":
                    while True:
                        message = input("Message: ")
                        if message == "exit":
                            break
                        ssock.sendall(message.encode())
                        data = ssock.recv(1024)
                        print(f"Received: {data.decode()}")

                elif command == "update_visibility":
                    message_id = input("Enter message ID to update visibility: ")
                    users_list_str = input("Enter comma-separated usernames who can see the message: ")

                    if not message_id or not users_list_str:
                        print("Message ID and user list cannot be empty.")
                        continue

                    ssock.sendall(f"update_visibility {message_id} {users_list_str}".encode())
                    response = ssock.recv(1024).decode()
                    print(response)

if __name__ == '__main__':
    start_client()
