import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8070"  # The WebSocket server address
    async with websockets.connect(uri) as websocket:
        # Sending a test message to the WebSocket server
        test_message = "Hello, WebSocket server!"
        print(f"Sending: {test_message}")
        await websocket.send(test_message)

        # # Receiving and printing the server response (if any)
        # response = await websocket.recv()
        # print(f"Received from server: {response}")

        # Infinite loop to keep the client running and listening for messages from the server
        while True:
            try:
                response = await websocket.recv()
                print(f"Received from server: {response}")
            except websockets.exceptions.ConnectionClosed:
                print("Connection with server closed")
                break  # Exit the loop if the connection is closed

# Running the WebSocket client to test the connection and message exchange
asyncio.run(test_websocket())

# Running the WebSocket client to test the connection and message exchange
# asyncio.get_event_loop().run_until_complete(test_websocket())

        