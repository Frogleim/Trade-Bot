import warnings

warnings.filterwarnings(action='ignore')

import pandas as pd
import numpy as np
from binance.client import Client
import aiohttp
import logging

# Initialize the Binance client
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
client = Client(api_key, api_secret)
symbol = 'MATICUSDT'


# Function to fetch historical futures data
def fetch_futures_klines(symbol, interval, limit=500):
    klines =  client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df


def get_df_15m():
    df_15m =  fetch_futures_klines(symbol, Client.KLINE_INTERVAL_15MINUTE)
    df_15m['SMA21'] = df_15m['close'].rolling(window=21).mean()
    return df_15m['SMA21'].iloc[-1]


if __name__ == '__main__':
    sam = get_df_15m()
    print(sam)