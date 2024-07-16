import time
import pandas as pd
import numpy as np
from binance.client import Client
import aiohttp
import asyncio
import logging
import ta

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 7
long_period = 25
adx_period = 14
symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 month ago UTC'


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
        df['EMA_short'] = ta.trend.ema_indicator(df['close'], window=short_period)
        df['EMA_long'] = ta.trend.ema_indicator(df['close'], window=long_period)

        df.dropna(inplace=True)
        return df


async def check_signal():
    data = await calculate_indicators()

    data['Signal'] = 0
    data['Signal'] = np.where((data['EMA_short'] > data['EMA_long']) & (data['ADX'] > 25), 1,
                              np.where((data['EMA_short'] < data['EMA_long']) & (data['ADX'] > 25), -1, 0))

    data['Crossover'] = data['Signal'].diff()

    last_close_price = data['close'].iloc[-1]

    if data['Crossover'].iloc[-1] == 1:
        return 'Buy', last_close_price
    elif data['Crossover'].iloc[-1] == -1:
        return 'Sell', last_close_price
    else:
        return 'Hold', 0.0


