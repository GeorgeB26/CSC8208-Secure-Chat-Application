from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    ip_address: str
    username: str
    message: str

# Define a route to receive messages
@app.post("/receive_message/")
async def receive_message(message: Message):
    """
    Receives a JSON message with an IP address and a message.
    """
    try:
        client2_ip = message.ip_address
        received_message = message.message
        
        # Print the received IP address and message
        print("Received data:")
        print(f"IP address: {client2_ip}")
        print(f"Message: {received_message}")
        
        return {"status": "Message received successfully"}
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
