import time
import pandas as pd
import numpy as np
from binance.client import Client
import aiohttp
import asyncio
import logging
import ta
from . import logging_settings

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 5
long_period = 8
adx_period = 14
atr_period = 14  # ATR period
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
        logging_settings.error_logs_logger.error(f'Error fetching klines: {e}')
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

async def check_signal():
    data = await calculate_indicators()

    data['Signal'] = 0
    data['Signal'] = np.where((data['EMA_Short'] > data['EMA_Long']) & (data['ADX'] > 25), 1,
                              np.where((data['EMA_Short'] < data['EMA_Long']) & (data['ADX'] > 25), -1, 0))

    data['Crossover'] = data['Signal'].diff()

    last_close_price = data['close'].iloc[-1]
    short_ema = data["EMA_Short"].iloc[-1]
    long_ema = data["EMA_Long"].iloc[-1]
    latest_atr = data['ATR'].iloc[-1]  # Get the latest ATR value

    if short_ema > long_ema:
        logging_settings.system_log.warning("Waiting for downtrend!")
        while True:
            data = await calculate_indicators()
            short_ema = data["EMA_Short"].iloc[-1]
            long_ema = data["EMA_Long"].iloc[-1]
            last_close_price = data['close'].iloc[-1]
            latest_atr = data['ATR'].iloc[-1]

            logging_settings.system_log.warning('EMA has not crossed yet')
            if short_ema < long_ema and float(atr_period) >0.0022:
                logging_settings.system_log.warning('EMA crosses')
                if last_close_price < long_ema:
                    return 'Sell', last_close_price, latest_atr
            await asyncio.sleep(20)  # Adjust the sleep time as needed

    elif short_ema < long_ema:
        logging_settings.system_log.warning("Waiting for uptrend!")
        while True:
            data = await calculate_indicators()
            short_ema = data["EMA_Short"].iloc[-1]
            long_ema = data["EMA_Long"].iloc[-1]
            last_close_price = data['close'].iloc[-1]
            latest_atr = data['ATR'].iloc[-1]

            logging_settings.system_log.warning('EMA has not crossed yet')
            if short_ema > long_ema and float(atr_period) > 0.0022:
                logging_settings.system_log.warning('EMA crosses')
                if last_close_price > long_ema:
                    return "Buy", last_close_price, latest_atr
            await asyncio.sleep(20)  # Adjust the sleep time as needed

    else:
        return 'Hold', last_close_price, latest_atr

async def main():
    while True:
        result = await check_signal()
        print(result)

if __name__ == '__main__':
    asyncio.run(main())
