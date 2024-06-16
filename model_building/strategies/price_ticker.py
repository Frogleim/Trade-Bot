import threading
import json
import asyncio
import websockets


class PriceStreaming():
    def __init__(self, url):
        self.latest_price = None
        self.url = url

    async def connect(self, stop_event):
        async with websockets.connect(self.url) as websocket:
            async for message in websocket:
                data = json.loads(message)
                self.proccess_message(data)
                if stop_event.is_set():
                    break

    def proccess_message(self, data):
        price = data['p']
        self.latest_price = price
        print(price)

    async def get_latest_price(self):
        while self.latest_price is None:
            await asyncio.sleep(0.1)
        return self.latest_price


if __name__ == '__main__':
    price_stream = PriceStreaming('wss://fstream.binance.com/ws/maticusdt@markPrice')
    threading.Thread(target=price_stream).start()

    # Example of how to get the latest price from another part of the code
    import time

    while True:
        latest_price = price_stream.get_latest_price()
        if latest_price is not None:
            print(f"Latest Price: {latest_price}")
        time.sleep(1)