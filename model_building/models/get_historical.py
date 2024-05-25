from binance.client import Client
from datetime import datetime, timedelta
import pandas as pd

# Your Binance API key and secret
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'

client = Client(API_KEY, API_SECRET)


def get_historical_klines(symbol, interval, start_str, end_str=None):
    """Get historical kline data from Binance"""
    return client.futures_historical_klines(symbol, interval, start_str, end_str)


# Define parameters
symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = (datetime.now() - timedelta(days=730)).strftime('%d %b %Y %H:%M:%S')  # 2 years ago
end_str = datetime.now().strftime('%d %b %Y %H:%M:%S')  # Now

# Fetch historical data
klines = get_historical_klines(symbol, interval, start_str, end_str)

# Convert the klines data to a Pandas DataFrame
df = pd.DataFrame(klines, columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
])

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Save to a CSV file
df.to_csv('./historical_data/MATICUSDT_15min_data.csv')

print("Data saved to MATICUSDT_15min_data.csv")
