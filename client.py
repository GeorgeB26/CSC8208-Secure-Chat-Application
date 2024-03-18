# Code for everything required for the client. Ability to send messages, encrypt and decrypt sent messages.
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import zipfile


username = ""
message = ""
decMessage = ""
filename = ""
zip_file_send = ""
save_directory = ""


def generate_key_pair():
    key_size = 2048  # Should be at least 2048

    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )

    public_key = private_key.public_key()
    return private_key, public_key


private_key, public_key = generate_key_pair()


def zip_file(filename):
    zipfile.ZipFile(zip_file_send, mode='w').write(filename)
# TODO: Ensure this can take user input to select a file from their machine,then pass to encryption before sending.


def unzip_file_save(dec_zip_file):
    with zipfile.ZipFile(dec_zip_file, 'r') as zip_ref:
        zip_ref.extractall(save_directory)


def encrypt_file(zip_file_send, public_key):
    return public_key.encrypt(
        zip_file_send,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decrypt_file(enc_zip_file, private_key):
    try:
        dec_zip_file = private_key.decrypt(
            enc_zip_file,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return dec_zip_file
    except ValueError:
        return "Failed to Decrypt"


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
    print("Welcome to the application, please type 'Exit' to leave.")
    while message == "":
        message = input("Enter Message: ")
        filename = input("Enter filepath to send: ")

    if message == "":
        print("No message provided")
    elif message == "Exit":
        break
    else:
        print("Message Accepted, sending...")
        message = message.encode(encoding='UTF-8')
        encMessage = encrypt(message, public_key)
        decMessage = decrypt(encMessage, private_key)
        zip_file(filename)
        enc_zip_file = encrypt_file(zip_file_send, public_key)
        dec_zip_file = decrypt_file(enc_zip_file,private_key)

        if message == decMessage:
            print("Message arrived unedited")
        else:
            print("Message has been edited in transit")
        print(message.decode())
        print(encMessage)
        print(username, "-->", decMessage.decode())
        save_directory = input("Enter filepath to save sent file: ")
        unzip_file_save(save_directory)
        message = ""
