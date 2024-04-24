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

    last_price = close.iloc[-1]
    signal_price = last_price
    if ema_short.iloc[-1] > ema_long.iloc[-1] and rsi.iloc[-1] < 30:
        return "Buy", signal_price
    elif ema_short.iloc[-1] < ema_long.iloc[-1] and rsi.iloc[-1] > 70:
        return "Sell", signal_price
    else:
        return "Hold", signal_price


# Example usage
if __name__ == '__main__':
    symbol = 'MATICUSDT'

    df = get_latest_candlestick(symbol)
    signal, price = generate_signal(df)
    print(f"Signal: {signal}, at Price: {price}")
