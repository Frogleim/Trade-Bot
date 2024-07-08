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


# Function to fetch historical futures data
async def fetch_futures_klines(symbol, interval, limit=500):
    klines = await client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df


class SMA21:
    def __init__(self, symbol):
        self.symbol = symbol

    async def get_df_15m(self):
        df_15m = await fetch_futures_klines(self.symbol, Client.KLINE_INTERVAL_15MINUTE)

        df_15m['SMA21'] = df_15m['close'].rolling(window=21).mean()

        # Define trigger zones
        trigger_offset = 0.0001  # Adjust this based on your needs
        df_15m['up_trigger_zone'] = df_15m['SMA21'] + trigger_offset
        df_15m['down_trigger_zone'] = df_15m['SMA21'] - trigger_offset

        # Initialize columns for signals and states
        df_15m['Buy_Signal'] = 0
        df_15m['Sell_Signal'] = 0
        df_15m['State'] = 'neutral'

        # Logic to generate signals
        for i in range(21, len(df_15m)):
            if df_15m['State'].iloc[i - 1] == 'neutral':
                if df_15m['close'].iloc[i] < df_15m['down_trigger_zone'].iloc[i]:
                    df_15m['State'].iloc[i] = 'waiting_for_up'
                elif df_15m['close'].iloc[i] > df_15m['up_trigger_zone'].iloc[i]:
                    df_15m['State'].iloc[i] = 'waiting_for_down'
                else:
                    df_15m['State'].iloc[i] = 'neutral'
            elif df_15m['State'].iloc[i - 1] == 'waiting_for_up':
                if df_15m['close'].iloc[i] > df_15m['up_trigger_zone'].iloc[i]:  # RSI confirmation
                    df_15m['Buy_Signal'].iloc[i] = 1
                    df_15m['State'].iloc[i] = 'neutral'
                elif df_15m['close'].iloc[i] < df_15m['down_trigger_zone'].iloc[i]:
                    df_15m['Sell_Signal'].iloc[i] = 1
                    df_15m['State'].iloc[i] = 'neutral'
                else:
                    df_15m['State'].iloc[i] = 'waiting_for_up'
            elif df_15m['State'].iloc[i - 1] == 'waiting_for_down':
                if df_15m['close'].iloc[i] < df_15m['down_trigger_zone'].iloc[i]:  # RSI confirmation
                    df_15m['Sell_Signal'].iloc[i] = 1
                    df_15m['State'].iloc[i] = 'neutral'
                elif df_15m['close'].iloc[i] > df_15m['up_trigger_zone'].iloc[i]:
                    df_15m['Buy_Signal'].iloc[i] = 1
                    df_15m['State'].iloc[i] = 'neutral'
                else:
                    df_15m['State'].iloc[i] = 'waiting_for_down'
        latest_row = \
            df_15m[
                ['close', 'SMA21', 'up_trigger_zone', 'down_trigger_zone', 'Buy_Signal', 'Sell_Signal', 'State']].iloc[
                -1]
        latest_row = latest_row.astype(object)


        return latest_row


    async def check_signal(self):
        df = await self.get_df_15m()

if __name__ == '__main__':
    symbol = 'MATICUSDT'
    sma = SMA21(symbol)
    latest = sma.get_df_15m()
    print(type(float(latest['close'])))
