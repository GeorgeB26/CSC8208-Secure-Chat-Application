# Code for everything required for the client. Ability to send messages, encrypt and decrypt sent messages.
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


username = ""
message = ""


def generate_key_pair():
    key_size = 2048  # Should be at least 2048

    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )

    public_key = private_key.public_key()
    return private_key, public_key


private_key, public_key = generate_key_pair()


def encrypt(message, public_key):
    return public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decrypt(encMessage, private_key):
    try:
        decMessage = private_key.decrypt(
            encMessage,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decMessage
    except ValueError:
        return "Failed to Decrypt"


while username == "":
    username = input("Enter Username: ")

if username == "":
    print("No username provided")
else:
    print("Username Accepted")

while True:
    while message == "":
        message = input("Enter Message: ")

    if message == "":
        print("No message provided")
    else:
        print("Message Accepted, sending...")
        message = message.encode(encoding='UTF-8')
        encMessage = encrypt(message, public_key)
        decMessage = decrypt(encMessage, private_key)
        print(message)
        print(encMessage)
        print(username, "-->", decMessage)
        message = input("Enter Message: ")

    if message == "Exit":
        break
