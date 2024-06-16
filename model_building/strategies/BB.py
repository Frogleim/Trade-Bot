import time
import pandas as pd
import os
import logging
import sys
import asyncio
import aiohttp
from binance.client import Client
from binance.enums import *

from db import DataBase

# Binance API setup
my_db = DataBase()
api_key, api_secret = my_db.get_binance_keys()
client = Client(api_key, api_secret)

interval = '15m'  # Use '15m' for 15-minute intervals
length = 20
num_std_dev = 2


async def fetch_klines(session, symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f'Error fetching klines: {e}')
        return []


async def fetch_ticker(session, symbol):
    url = f'https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f'Error fetching ticker: {e}')
        return {}


async def calculate_bollinger_bands(session, interval, length, num_std_dev):
    klines = await fetch_klines(session, 'MATICUSDT', interval)
    if not klines:
        return pd.Series([None, None, None], index=['sma', 'upper_band', 'lower_band'])

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
    async with aiohttp.ClientSession() as session:
        bollinger_values = await calculate_bollinger_bands(session, interval=interval, length=length,
                                                           num_std_dev=num_std_dev)
        upper_band, lower_band = float(bollinger_values['upper_band']), float(bollinger_values['lower_band'])
        logging.info(f'Bollinger Bands - Upper: {upper_band}, Lower: {lower_band}')

        ticker = await fetch_ticker(session, "MATICUSDT")
        live_price = float(ticker.get('price', 0))
        logging.info(f'Price: {live_price} --- Upper Band: {upper_band}, Lower Band: {lower_band}')

        if live_price > upper_band + 0.0010:
            return 'Buy', live_price
        elif live_price < lower_band - 0.0010:
            return 'Sell', live_price
        else:
            return 'Hold', live_price


# Running the asynchronous function
async def main():
    result = await check_sma()
    return result


if __name__ == '__main__':
    res = asyncio.run(main())
    print(res)