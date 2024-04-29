import pandas as pd
from binance.client import Client
from binance.enums import *
import ta

# Constants
API_KEY = 'your_api_key_here'
API_SECRET = 'your_api_secret_here'
SYMBOL = 'MATICUSDT'
TIME_INTERVAL = Client.KLINE_INTERVAL_5MINUTE

# Initialize client
client = Client(API_KEY, API_SECRET)


def fetch_candles(symbol, interval, lookback):
    candles = client.futures_klines(symbol=symbol, interval=interval, limit=lookback)
    df = pd.DataFrame(candles)
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                  'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df['close'] = pd.to_numeric(df['close'])
    df['low'] = pd.to_numeric(df['low'])
    df['high'] = pd.to_numeric(df['high'])
    df['open'] = pd.to_numeric(df['open'])
    return df


def calculate_bollinger(df, window_size=20, num_of_std=2):
    indicator_bb = ta.volatility.BollingerBands(df['close'], window=window_size, window_dev=num_of_std)
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()
    return df


def generate_signals(df):
    df['signal'] = 0
    df.loc[df['close'] > df['bb_bbh'], 'signal'] = -1  # Sell signal
    df.loc[df['close'] < df['bb_bbl'], 'signal'] = 1  # Buy signal
    return df


def main():
    data = fetch_candles(SYMBOL, TIME_INTERVAL, 100)
    data_with_bb = calculate_bollinger(data)
    signals = generate_signals(data_with_bb)

    # Print last few signals
    print(signals[['close', 'bb_bbl', 'bb_bbh', 'signal']].tail())


if __name__ == "__main__":
    main()
