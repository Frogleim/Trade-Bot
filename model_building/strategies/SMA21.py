import asyncio
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



async def fetch_klines(session, symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f'Error fetching klines: {e}')
        return []


class SMA21:
    def __init__(self, symbol):
        self.symbol = symbol
        self.interval = '15m'

    async def calculate_sma(self):
        async with aiohttp.ClientSession() as session:
            df = await fetch_klines(session, symbol=self.symbol, interval=self.interval)
            df = pd.DataFrame(df, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            return df

    async def get_df_15m(self):
        df_15m = await self.calculate_sma()
        df_15m['SMA21'] = df_15m['close'].rolling(window=21).mean()

        # Define trigger zones
        trigger_offset = 0.00005  # Adjust this based on your needs
        df_15m['up_trigger_zone'] = df_15m['SMA21'] + trigger_offset
        df_15m['down_trigger_zone'] = df_15m['SMA21'] - trigger_offset

        # Initialize columns for signals and states
        df_15m['Signal'] = 0  # Combined signal column
        df_15m['State'] = 'neutral'

        # Logic to generate signals
        for i in range(21, len(df_15m)):
            if df_15m['State'].iloc[i - 1] == 'neutral':
                if df_15m['close'].iloc[i] < df_15m['down_trigger_zone'].iloc[i]:
                    df_15m['State'].iloc[i] = 'waiting_for_up'
                elif df_15m['close'].iloc[i] > df_15m['up_trigger_zone'].iloc[i]:
                    df_15m['State'].iloc[i] = 'waiting_for_down'

            elif df_15m['State'].iloc[i - 1] == 'waiting_for_up':
                if df_15m['close'].iloc[i] > df_15m['up_trigger_zone'].iloc[i] and df_15m['low'].iloc[i] > df_15m['SMA21'].iloc[i]:
                    df_15m['Signal'].iloc[i] = 1  # Buy
                    df_15m['State'].iloc[i] = 'neutral'
                else:
                    df_15m['State'].iloc[i] = 'waiting_for_up'

            elif df_15m['State'].iloc[i - 1] == 'waiting_for_down':
                if df_15m['close'].iloc[i] < df_15m['down_trigger_zone'].iloc[i] and df_15m['high'].iloc[i] < df_15m['SMA21'].iloc[i]:
                    df_15m['Signal'].iloc[i] = -1  # Sell
                    df_15m['State'].iloc[i] = 'neutral'
                else:
                    df_15m['State'].iloc[i] = 'waiting_for_down'

        signal_map = {
            1.0: 'Buy',
            -1.0: 'Sell',
            0.0: 'Hold'
        }
        df_15m['Signal'] = df_15m['Signal'].map(signal_map)

        return df_15m['Signal'].iloc[-1]

        # Mapping signals using signal_map




async def main():
    sma21 = SMA21('MATICUSDT')
    result = await sma21.get_df_15m()
    print(result)


if __name__ == '__main__':
    asyncio.run(main())