import warnings

warnings.filterwarnings(action='ignore')
import pandas as pd
import numpy as np
from binance.client import Client

# Initialize the Binance client
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
client = Client(api_key, api_secret)


# Function to fetch historical futures data
def fetch_futures_klines(symbol, interval, limit=500):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df


# Define the symbol
symbol = 'MATICUSDT'

# Fetch historical data for different time frames
df_15m = fetch_futures_klines(symbol, Client.KLINE_INTERVAL_15MINUTE)
df_1h = fetch_futures_klines(symbol, Client.KLINE_INTERVAL_1HOUR)
df_4h = fetch_futures_klines(symbol, Client.KLINE_INTERVAL_4HOUR)

# Calculate SMA 21
df_15m['SMA21'] = df_15m['close'].rolling(window=21).mean()
df_1h['SMA21'] = df_1h['close'].rolling(window=21).mean()
df_4h['SMA21'] = df_4h['close'].rolling(window=21).mean()

# Generate signals on 15-minute chart
df_15m['Signal'] = 0
df_15m['Signal'][21:] = np.where(df_15m['close'][21:] > df_15m['SMA21'][21:], 1, 0)
df_15m['Position'] = df_15m['Signal'].diff()

# Confirmation from 1-hour chart
df_1h['Above_SMA21'] = df_1h['close'] > df_1h['SMA21']

# Context from 4-hour chart
df_4h['Above_SMA21'] = df_4h['close'] > df_4h['SMA21']


# Function to check confirmation and context
def confirm_and_context(timestamp):
    hour = timestamp.floor('H')
    four_hour = timestamp.floor('4H')
    if hour in df_1h.index and four_hour in df_4h.index:
        return df_1h.loc[hour, 'Above_SMA21'] and df_4h.loc[four_hour, 'Above_SMA21']
    return False


df_15m['Confirmed_Signal'] = df_15m.apply(lambda row: row['Signal'] if confirm_and_context(row.name) else 0, axis=1)

# Display the signals
print(df_15m.tail())
