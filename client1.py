import requests
import json

# Replace this with the actual IP address where main.py is running
server_url = "http://localhost:8000/receive_message/"

# Replace this with the IP address of client2.py
client2_url = "http://localhost:8001/receive_message/"

# JSON data to be sent
data = {"ip_address": "localhost", "username": "vishnu", "message": "hello, how are you doing?"}

print("Sending data to server:")
print(json.dumps(data, indent=4))  # Print the data being sent to the server

try:
    # Post the JSON data to the server
    response = requests.post(server_url, json=data)
    response.raise_for_status()
    print("Response from server:")
    print(response.json())  # Print the response from the server
except requests.RequestException as e:
    print(f"Failed to send message to server: {e}")
