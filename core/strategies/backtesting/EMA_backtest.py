import pandas as pd
import numpy as np
import aiohttp
import asyncio
import logging
from binance.client import Client
import ta

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 5
long_period = 8
adx_period = 14
atr_period = 14
symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 month ago UTC'
starting_capital = 20

async def fetch_klines(session, symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f'Error fetching klines: {e}')
        return []

async def calculate_indicators():
    async with aiohttp.ClientSession() as session:
        klines = await fetch_klines(session, symbol=symbol, interval=interval)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        # Calculate ADX
        df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)

        # Calculate EMAs
        df['EMA_Short'] = df['close'].ewm(span=short_period, adjust=False).mean()
        df['EMA_Long'] = df['close'].ewm(span=long_period, adjust=False).mean()

        # Calculate ATR
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)

        df.dropna(inplace=True)
        return df

async def backtest():
    data = await calculate_indicators()
    capital = starting_capital
    position = None
    buy_price = 0

    for i in range(1, len(data)):
        short_ema = data['EMA_Short'].iloc[i]
        long_ema = data['EMA_Long'].iloc[i]
        adx = data['ADX'].iloc[i]
        close = data['close'].iloc[i]
        atr = data['ATR'].iloc[i]

        if short_ema > long_ema and adx > 25:
            if position != 'long':
                if position == 'short':
                    capital += (buy_price - close)
                position = 'long'
                buy_price = close
        elif short_ema < long_ema and adx > 25:
            if position != 'short':
                if position == 'long':
                    capital += (close - buy_price)
                position = 'short'
                buy_price = close

    return capital

async def main():
    final_capital = await backtest()
    print(f"Final capital: {final_capital}")

if __name__ == '__main__':
    asyncio.run(main())
