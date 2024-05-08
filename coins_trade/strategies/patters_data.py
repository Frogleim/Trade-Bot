from binance.client import Client
import pandas as pd

api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Initialize the Binance client
client = Client(api_key, api_secret)

# Fetch historical candlestick data for MATICUSDT on Binance Futures
# Set the interval to '1h' for hourly data. Other options include '1m' for minute, '1d' for daily, etc.
candles = client.futures_klines(symbol='MATICUSDT', interval=Client.KLINE_INTERVAL_1HOUR)

# Create a DataFrame
# The columns returned from Binance are: open time, open, high, low, close, volume, close time, and several others
columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
df = pd.DataFrame(candles, columns=columns)

# Convert timestamp to readable date
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

# Convert columns to appropriate data types
df['open'] = df['open'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['close'] = df['close'].astype(float)
df['volume'] = df['volume'].astype(float)

print(df.head())  # Display the first few rows of the DataFrame

# Save the data to a CSV file
df.to_csv('MATICUSDT_hourly_data.csv', index=False)