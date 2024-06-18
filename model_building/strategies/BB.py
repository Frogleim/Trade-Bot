import time
import pandas as pd
import os
import logging
import sys
import asyncio
import ccxt.async_support as ccxt
import aiohttp
from coins_trade.miya import logging_settings
from db import DataBase

# Initialize database and get API keys
my_db = DataBase()
api_key, api_secret = my_db.get_binance_keys()

# Setup ccxt binance client
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultType': 'future',
    },
})

interval = '15m'  # Use '15m' for 15-minute intervals
length = 20
num_std_dev = 2

async def fetch_klines(symbol, interval):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=interval)
        return ohlcv
    except ccxt.BaseError as e:
        logging.error(f'Error fetching klines: {e}')
        return []

async def fetch_ticker(symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return ticker
    except ccxt.BaseError as e:
        logging.error(f'Error fetching ticker: {e}')
        return {}

async def calculate_bollinger_bands(interval, length, num_std_dev):
    klines = await fetch_klines('MATIC/USDT', interval)
    if not klines:
        return pd.Series([None, None, None], index=['sma', 'upper_band', 'lower_band'])

    close_prices = [kline[4] for kline in klines]
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
    bollinger_values = await calculate_bollinger_bands(interval=interval, length=length, num_std_dev=num_std_dev)
    upper_band, lower_band = float(bollinger_values['upper_band']), float(bollinger_values['lower_band'])
    logging.info(f'Bollinger Bands - Upper: {upper_band}, Lower: {lower_band}')

    ticker = await fetch_ticker("MATIC/USDT")
    live_price = float(ticker.get('last', 0))
    print(live_price)
    logging_settings.system_log.info(f'Price: {live_price} --- Upper Band: {upper_band}, Lower Band: {lower_band}')

    if live_price > upper_band + 0.0008:
        return 'Sell', live_price
    elif live_price < lower_band - 0.0008:
        return 'Buy', live_price
    else:
        return 'Hold', live_price

# Running the asynchronous function
async def main():
    result = await check_sma()
    await exchange.close()  # Close the ccxt client session
    return result

if __name__ == '__main__':
    res = asyncio.run(main())
    print(res)
