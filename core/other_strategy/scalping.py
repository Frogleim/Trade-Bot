from binance.client import Client
import pandas as pd
import numpy as np
# Binance API credentials
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

# Initialize the Binance client
client = Client(api_key, api_secret)


def get_historical_data(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                         'taker_buy_quote_asset_volume', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data['close'] = data['close'].astype(float)
    return data


def trend_following_strategy(symbol, short_window, long_window):
    data = get_historical_data(symbol, interval='1h', limit=200)  # Adjust limit based on your needs

    # Calculate short-term and long-term moving averages
    data['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1, center=False).mean()
    data['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Generate signals based on moving average crossovers
    data['signal'] = 0.0
    data['signal'][short_window:] = np.where(data['short_mavg'][short_window:] > data['long_mavg'][short_window:], 1.0,
                                             0.0)

    # Generate trading orders based on signals
    data['positions'] = data['signal'].diff()

    # Execute trading orders (buy/sell signals)
    for index, row in data.iterrows():
        if row['positions'] == 1.0:
            print(f"Buy {symbol} at {row['close']}")
            # Add your buy order logic here using the Binance API
        elif row['positions'] == -1.0:
            print(f"Sell {symbol} at {row['close']}")
            # Add your sell order logic here using the Binance API


# Example usage
symbol_to_trade = 'BTCUSDT'
short_window_size = 50
long_window_size = 200

trend_following_strategy(symbol_to_trade, short_window_size, long_window_size)
