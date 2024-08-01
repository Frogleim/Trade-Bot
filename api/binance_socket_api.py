import asyncio
import websockets
import ssl
import json

async def listen():
    url = "wss://fstream.binance.com/ws/maticusdt@kline_15m"
    
    # Create an SSL context with certificate verification disabled
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with websockets.connect(url, ssl=ssl_context) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(data)

asyncio.get_event_loop().run_until_complete(listen())
