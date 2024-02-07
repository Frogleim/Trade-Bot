import asyncio
from binance.client import AsyncClient
import pandas as pd
import logging_settings


async def get_bollinger_bands(client, symbol, interval, length, num_std_dev, queue):
    try:
        klines = await client.futures_klines(symbol=symbol, interval=interval)
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        klines = await client.futures_klines(symbol=symbol, interval=interval)

    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = df['close'].rolling(window=length).mean()
    df['std_dev'] = df['close'].rolling(window=length).std()
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])
    await queue.put((symbol, df))


async def display_bollinger_bands(client, symbols, interval, length, num_std_dev):
    while True:
        queue = asyncio.Queue()
        tasks = [get_bollinger_bands(client, symbol, interval, length, num_std_dev, queue) for symbol in symbols]
        await asyncio.gather(*tasks)

        results = []
        while not queue.empty():
            results.append(await queue.get())

        for symbol, df in results:
            last_row = df.iloc[-1]
            print(f"Last upper band for {symbol}: {last_row['upper_band']}")
            print(f"Last lower band for {symbol}: {last_row['lower_band']}")

        await asyncio.sleep(1)  # Adjust the sleep time as needed


async def main():
    client = await AsyncClient.create()
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  # Add more symbols as needed
    interval = '1h'  # Interval for klines
    length = 20  # Length for Bollinger Bands calculation
    num_std_dev = 2  # Number of standard deviations for Bollinger Bands

    await display_bollinger_bands(client, symbols, interval, length, num_std_dev)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
