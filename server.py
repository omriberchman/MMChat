import asyncio
import websockets

# Maintain a list of connected clients
connected_clients = set()

async def handle_websocket(websocket, path):
    # This function will be called whenever a new WebSocket connection is established.
    print(f"Client connected from {websocket.remote_address}")

    # Add the new client to the set of connected clients
    connected_clients.add(websocket)

    try:
        while True:
            message = await websocket.recv()
            print(f"~~~  Received message from {websocket.remote_address}: {message}  ~~~")

            # Broadcast the message to all connected clients except the sender
            for client in connected_clients:
                if client != websocket and client.open:
                    # await client.send(f"from {websocket.remote_address}: {message[:25:]}") # With IP, not needed for the chat.
                    await client.send({message}) # just the content.

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed by {websocket.remote_address}")
        # Remove the client from the set of connected clients
        connected_clients.remove(websocket)

async def main():
    server = await websockets.serve(handle_websocket, "0.0.0.0", 8765)
    print("WebSocket server started on ws://localhost:8765")

    # Keep the server running indefinitely
    await server.wait_closed()

# Run the WebSocket server
asyncio.run(main())
