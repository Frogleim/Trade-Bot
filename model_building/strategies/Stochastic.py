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
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# Define the symbol
symbol = 'MATICUSDT'

# Fetch historical data for 15-minute time frame
df_15m = fetch_futures_klines(symbol, Client.KLINE_INTERVAL_15MINUTE)

# Calculate Stochastic Oscillator
look_back_period = 14
df_15m['Lowest Low'] = df_15m['low'].rolling(window=look_back_period).min()
df_15m['Highest High'] = df_15m['high'].rolling(window=look_back_period).max()
df_15m['%K'] = (df_15m['close'] - df_15m['Lowest Low']) / (df_15m['Highest High'] - df_15m['Lowest Low']) * 100
df_15m['%D'] = df_15m['%K'].rolling(window=3).mean()

# Drop NaN values
df_15m.dropna(inplace=True)

# Generate signals
oversold_threshold = 20
overbought_threshold = 80

df_15m['Buy_Signal'] = np.where((df_15m['%K'] < oversold_threshold) & (df_15m['%K'].shift(1) < df_15m['%D'].shift(1)) & (df_15m['%K'] > df_15m['%D']), 1, 0)
df_15m['Sell_Signal'] = np.where((df_15m['%K'] > overbought_threshold) & (df_15m['%K'].shift(1) > df_15m['%D'].shift(1)) & (df_15m['%K'] < df_15m['%D']), -1, 0)

# Combine signals into one column
df_15m['Signal'] = df_15m['Buy_Signal'] + df_15m['Sell_Signal']

# Display the DataFrame with Stochastic Oscillator and signals
print(df_15m[['close', '%K', '%D', 'Buy_Signal', 'Sell_Signal', 'Signal']].tail())
