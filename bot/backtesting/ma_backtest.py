import pandas as pd
import numpy as np
from binance.client import Client

# Initialize Binance client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Define the buy and sell signals based on moving average crossover
def generate_signals(data, short_window=50, long_window=200):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    # Calculate the moving averages
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1).mean()

    # Generate buy signals
    signals.loc[signals['short_mavg'] > signals['long_mavg'], 'signal'] = 1

    # Generate sell signals
    signals.loc[signals['short_mavg'] < signals['long_mavg'], 'signal'] = -1

    return signals

# Define the backtest function
def backtest(data, signals, initial_capital=40):
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    positions['asset'] = initial_capital * signals['signal'].shift()

    # Calculate the portfolio value
    portfolio = positions.multiply(data['close'], axis=0)
    portfolio['cash'] = initial_capital - (positions.diff().multiply(data['close'], axis=0)).cumsum()

    portfolio['total'] = portfolio['asset'] + portfolio['cash']
    portfolio['returns'] = portfolio['total'].pct_change()
    return portfolio

# Load historical price data into a DataFrame using Binance API
symbol = 'BTCUSDT'  # Example symbol
klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2020", "1 Jan, 2023")
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data.set_index('timestamp', inplace=True)
data = data.astype(float)

# Generate the signals
signals = generate_signals(data)

# Run the backtest
portfolio = backtest(data, signals)

# Print the backtest results
print(portfolio)

