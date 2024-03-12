# Code for everything required for the client. Ability to send messages, encrypt and decrypt sent messages.
from cryptography.fernet import Fernet


key = Fernet.generate_key()
fernet = Fernet(key)
username = ""
message = ""


while username == "":
    username = input("Enter Username: ")

if username == "":
    print("No username provided")
else:
    print("Username Accepted")

while message == "":
    message = input("Enter Message: ")

if message == "":
    print("No message provided")
else:
    print("Message Accepted, sending...")

encMessage = fernet.encrypt(message.encode())
decMessage = fernet.decrypt(encMessage).decode()

print(message)
print(encMessage)
print(username, "-->", decMessage)
