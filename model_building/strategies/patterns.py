import warnings
from candlestick import candlestick

warnings.filterwarnings(action='ignore')
from binance.client import Client
import pandas as pd

client = Client()


def fetch_futures_klines(symbol, interval, limit=500):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df


if __name__ == '__main__':
    symbol = 'MATICUSDT'
    interval = '15m'

    df = fetch_futures_klines(
        symbol=symbol,
        interval=interval
    )
    # print(df)
    pattern_candle = candlestick.piercing_pattern(df, target='result')
    print(pattern_candle)