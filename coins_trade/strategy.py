import pandas as pd
import numpy as np
from binance.client import Client

client = Client(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET')


def get_latest_candlestick(symbol):
    candles = client.futures_klines(symbol=symbol, interval='5m', limit=100)
    df = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df


def calculate_ema(prices, window):
    return prices.ewm(span=window, adjust=False).mean()


def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def generate_signal(df):
    close = df['close']
    ema_short = calculate_ema(close, 12)
    ema_long = calculate_ema(close, 26)
    rsi = calculate_rsi(close, 14)

    # Implement MACD
    macd = ema_short - ema_long
    signal_line = calculate_ema(macd, 9)

    # Implement ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.DataFrame([high_low, high_close, low_close]).max()
    atr = tr.rolling(window=14).mean()

    last_price = close.iloc[-1]
    if macd.iloc[-1] > signal_line.iloc[-1] and rsi.iloc[-1] > 50:
        return "Buy", last_price
    elif macd.iloc[-1] < signal_line.iloc[-1] and rsi.iloc[-1] < 50:
        return "Sell", last_price
    else:
        return "Hold", last_price


if __name__ == '__main__':
    symbol = 'MATICUSDT'
    df = get_latest_candlestick(symbol)
    signal, price = generate_signal(df)
    print(f"Signal: {signal}, at Price: {price}")
