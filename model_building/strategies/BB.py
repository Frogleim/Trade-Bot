import time
import pandas as pd
import asyncio
from binance.client import Client
import logging
import price_ticker
import threading

client = Client()
interval = '15m'  # Use '15m' for 15-minute intervals
length = 20
num_std_dev = 2


async def calculate_bollinger_bands(interval, length, num_std_dev):
    klines = client.futures_klines(symbol='MATICUSDT', interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})

    # Calculate SMA using pandas
    df['sma'] = df['close'].rolling(window=length).mean()

    # Calculate standard deviation
    df['std_dev'] = df['close'].rolling(window=length).std()

    # Calculate upper and lower Bollinger Bands
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])

    return df[['sma', 'upper_band', 'lower_band']].iloc[-1]


async def check_sma():
    stop_event = asyncio.Event()
    price_stream = price_ticker.PriceStreaming('wss://fstream.binance.com/ws/maticusdt@markPrice')
    price_stream_task = asyncio.create_task(price_stream.connect(stop_event))
    while not stop_event.is_set():
        latest_price = await price_stream.get_latest_price()

        bollinger_values = await calculate_bollinger_bands(interval=interval, length=length, num_std_dev=num_std_dev)

        upper_band, lower_band = float(bollinger_values['upper_band']), float(bollinger_values['lower_band'])

        logging.info(f'Price: {latest_price} --- Upper Band: {upper_band}, Lower Band: {lower_band}')
        print(f'Up Difference {upper_band + 0.001} Price: {float(latest_price)}')
        print(f'Low Difference {upper_band - 0.001} Price: {float(latest_price)}')

        if float(latest_price) > upper_band + 0.0008:
            print('Buy Signal')
            stop_event.is_set()
            return 'Buy', latest_price
        elif float(latest_price) < lower_band - 0.0008:
            print('Sell Signal')

            stop_event.is_set()
            return 'Sell', latest_price
        else:
            print('HOld')
            await asyncio.sleep(1)
    await price_stream_task



if __name__ == '__main__':
    while True:
        asyncio.run(check_sma())