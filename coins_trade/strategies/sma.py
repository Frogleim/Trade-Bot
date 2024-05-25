from binance.client import Client
from binance.enums import *
import pandas as pd

# Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Create a Binance client
client = Client(api_key, api_secret)


# Function to get historical data
def get_historical_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.futures_historical_klines(symbol, interval, lookback))
    frame = frame.iloc[:, 0:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame['Close'] = pd.to_numeric(frame['Close'])
    frame['Time'] = pd.to_datetime(frame['Time'], unit='ms')
    return frame


# Calculate SMAs
def calculate_smas(data, short_window, long_window):
    data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['Close'].rolling(window=long_window).mean()
    return data


# Strategy execution
def execute_strategy(symbol, interval, lookback, short_window, long_window):
    data = get_historical_data(symbol, interval, lookback)
    data = calculate_smas(data, short_window, long_window)

    # Check for SMA crossover
    buy_signal = (data['SMA_short'].iloc[-2] < data['SMA_long'].iloc[-2]) and (
                data['SMA_short'].iloc[-1] > data['SMA_long'].iloc[-1])
    sell_signal = (data['SMA_short'].iloc[-2] > data['SMA_long'].iloc[-2]) and (
                data['SMA_short'].iloc[-1] < data['SMA_long'].iloc[-1])

    # Get the current close price as the entry price for the signal
    entry_price = data['Close'].iloc[-1] if (buy_signal or sell_signal) else None
    if buy_signal:
        return "Buy", entry_price
    elif sell_signal:
        return "Sell", entry_price
    else:
        return 'Hold', entry_price


# Parameters

if __name__ == '__main__':
    symbol = 'MATICUSDT'
    interval = '1h'
    lookback = '30 day'
    short_window = 7  # Short term SMA window
    long_window = 25  # Long term SMA window

    # Run the strategy
