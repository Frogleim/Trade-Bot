import time

import pandas as pd
from binance.client import Client
import os
import logging
import sys

client = Client()
interval = '15m'  # Use '15m' for 15-minute intervals
length = 20
num_std_dev = 2


def calculate_bollinger_bands(interval, length, num_std_dev):
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


def check_sma():
    bollinger_values = calculate_bollinger_bands(interval=interval, length=length, num_std_dev=num_std_dev)
    upper_band, lower_band = float(bollinger_values['upper_band']), float(bollinger_values['lower_band'])
    print(upper_band, lower_band)
    live_price = float(client.futures_ticker(symbol="MATICUSDT")['lastPrice'])
    logging.info(f'Price: {live_price} --- Upper Band: {upper_band}, Lower Band: {lower_band}')

    if live_price > upper_band + 0.0015:
        return 'Buy', live_price
    elif live_price < lower_band - 0.0015:
        return 'Sell', live_price
    else:
        return 'Hold', 0.0
