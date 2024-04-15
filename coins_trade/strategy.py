import pandas as pd
import ccxt
from binance.client import Client
import numpy as np

long_entry_price = 0.00
short_entry_price = 0.00
client = Client(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET')


def get_signal():
    global long_entry_price, short_entry_price

    exchange = ccxt.binance({'option': {'defaultMarket': 'futures'}})
    symbol = 'MATIC/USDT'
    timeframe = '5m'
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['ema10'] = df['close'].ewm(span=10).mean()
    df['ema20'] = df['close'].ewm(span=20).mean()
    k_period, d_period = 14, 3
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    df['%K'] = 100 * (df['close'] - low_min) / (high_max - low_min)
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    short_period, long_period, signal_period = 12, 26, 9
    df['ema_short'] = df['close'].ewm(span=short_period).mean()
    df['ema_long'] = df['close'].ewm(span=long_period).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['signal_line'] = df['macd'].ewm(span=signal_period).mean()
    df['long_entry'] = (df['ema10'] > df['ema20']) & (df['%K'] > df['%D']) & (df['macd'] > df['signal_line'])
    df['long_exit'] = df['close'].pct_change() > 0.01  # 1% profit target as exit signal
    df['short_entry'] = (df['ema10'] < df['ema20']) & (df['%K'] < df['%D']) & (df['macd'] < df['signal_line'])
    df['short_exit'] = df['close'].pct_change() < -0.01  # 1% profit target as exit signal
    in_long_trade = False
    in_short_trade = False
    for index, row in df.iterrows():
        if row['long_entry'] and not in_long_trade:
            print(f"Enter long at {row['close']} USD")
            long_entry_price = row['close']
            in_long_trade = True
        elif row['long_exit'] and in_long_trade:
            print(f"Exit long at {row['close']} USD")
            in_long_trade = False
        if row['short_entry'] and not in_short_trade:
            print(f"Enter short at {row['close']} USD")
            short_entry_price = row['close']
            in_short_trade = True
        elif row['short_exit'] and in_short_trade:
            print(f"Exit short at {row['close']} USD")
            in_short_trade = False
    return long_entry_price, short_entry_price


def get_latest_candlestick(symbol):
    """Fetches the latest 5-minute candlestick data for the specified symbol."""
    candles = client.futures_klines(symbol=symbol, interval='5m', limit=20)
    latest_candle = candles[0]
    df = pd.DataFrame([latest_candle], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                                'close_time', 'quote_asset_volume', 'number_of_trades',
                                                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                                'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df.astype(float)


def calculate_sma(close_prices, window):
    """Calculates Simple Moving Average (SMA) for a specified window."""
    return close_prices.rolling(window=window).mean()


def generate_signal(symbol, short_window=20, long_window=50):
    """Generates a buy or sell signal along with the signal price based on SMA analysis of the latest candlestick."""
    latest_candle = get_latest_candlestick(symbol)
    close_prices = latest_candle['close']
    short_sma = calculate_sma(close_prices, short_window)
    long_sma = calculate_sma(close_prices, long_window)

    signal_price = latest_candle.iloc[-1]['close']

    if short_sma.iloc[-1] > long_sma.iloc[-1]:
        return "Buy", signal_price  # If short-term SMA is above long-term SMA, generate a buy signal
    else:
        return "Sell", signal_price  # Otherwise, generate a sell signal


def main():
    symbol = 'MATICUSDT'  # Example symbol (Bitcoin against USDT)
    signal, signal_price = generate_signal(symbol)  # Generate signal for the specified symbol
    print("Signal:", signal)
    print("Signal Price:", signal_price)
    return signal, signal_price


if __name__ == '__main__':
    get_signal()
