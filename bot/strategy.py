import pandas as pd
import ccxt
import db

long_entry_price = 0.00
short_entry_price = 0.00


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


if __name__ == '__main__':
    get_signal()
