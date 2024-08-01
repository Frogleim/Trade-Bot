import asyncio
import websockets
import ssl
import json
import pandas as pd
import time

async def hello_world():
    while True:
        print('Hello world')
        await asyncio.sleep(3)

async def fetch_ohlcv(symbol='maticusdt', timeframe='15m', limit=1000):
    url = f"wss://fstream.binance.com/ws/{symbol}@kline_{timeframe}"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    data_list = []
    
    async with websockets.connect(url, ssl=ssl_context) as websocket:
        while len(data_list) < limit:
            response = await websocket.recv()
            data = json.loads(response)
            kline = data['k']
            kline_data = {
                'timestamp': kline['t'],
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v'])
            }
            data_list.append(kline_data)
            print(data_list)

        print('Data grabbed successfully')
        df = pd.DataFrame(data_list)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df

async def main():
    df = await fetch_ohlcv(symbol='maticusdt', timeframe='15m', limit=1000)
    await hello_world()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(fetch_ohlcv()),
        loop.create_task(hello_world())
    ]
    loop.run_until_complete(asyncio.wait(tasks))
# Run the main function to fetch and print the DataFrame
