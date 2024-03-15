from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import requests
import json
import threading
import queue

app = FastAPI()

class Message(BaseModel):
    ip_address: str
    username: str
    message: str

# Create a message queue
message_queue = queue.Queue()

def forward_message():
    """
    Worker function to forward messages from the queue.
    """
    while True:
        try:
            message = message_queue.get()
            client2_url = f"http://{message['ip_address']}:8001/receive_message/"
            response = requests.post(client2_url, json=message)
            response.raise_for_status()
            print(f"Message forwarded to {message['ip_address']}: {message['message']}")
        except requests.RequestException as e:
            print(f"Failed to send message: {e}")

# Start the worker thread
worker_thread = threading.Thread(target=forward_message)
worker_thread.daemon = True
worker_thread.start()

# Define a route to receive JSON messages
@app.post("/receive_message/")
async def receive_message(message: Message = Body(...)):
    """
    Receives a JSON message with an IP address and a message.
    """
    # Extract data from the received message
    client2_ip = message.ip_address
    received_message = message.message

    # Print the received data for debugging purposes
    print("Received data in main.py:")
    print(f"IP address: {client2_ip}")
    print(f"Message: {received_message}")

    # Add the received message to the queue
    message_queue.put(message.dict())

    return {"status": "Message received and queued for forwarding"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
