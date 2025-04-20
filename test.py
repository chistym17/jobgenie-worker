import asyncio
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/recommendations"
    async with websockets.connect(uri) as websocket:
        # Send a query
        await websocket.send('{"query": "Recommend me frontend developer jobs"}')
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_ws())

asyncio.run(test_ws())