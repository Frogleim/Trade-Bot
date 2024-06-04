import pandas as pd
import numpy as np
from binance.client import Client
from binance.enums import HistoricalKlinesType


client = Client()


def detect_head_shoulder(df, window=3):
    roll_window = window
    # Create a rolling window for High and Low
    df['high_roll_max'] = df['high'].rolling(window=roll_window).max()
    df['low_roll_min'] = df['low'].rolling(window=roll_window).min()
    # Create a boolean mask for Head and Shoulder pattern
    mask_head_shoulder = ((df['high_roll_max'] > df['high'].shift(1)) & (df['high_roll_max'] > df['high'].shift(-1)) & (
            df['high'] < df['high'].shift(1)) & (df['high'] < df['high'].shift(-1)))
    # Create a boolean mask for Inverse Head and Shoulder pattern
    mask_inv_head_shoulder = ((df['low_roll_min'] < df['low'].shift(1)) & (df['low_roll_min'] < df['low'].shift(-1)) & (
            df['low'] > df['low'].shift(1)) & (df['low'] > df['low'].shift(-1)))
    # Create a new column for Head and Shoulder and its inverse pattern and populate it using the boolean masks
    df['head_shoulder_pattern'] = np.nan
    df.loc[mask_head_shoulder, 'head_shoulder_pattern'] = 'Head and Shoulder'
    df.loc[mask_inv_head_shoulder, 'head_shoulder_pattern'] = 'Inverse Head and Shoulder'
    return df


def fetch_binance_data(ticker, start_date, end_date, interval):
    klines = client.get_historical_klines(ticker, interval, start_date, end_date,
                                          klines_type=HistoricalKlinesType.FUTURES)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time',
        'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume',
        'Taker_buy_quote_asset_volume', 'Ignore'
    ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return data


if __name__ == '__main__':
    interval = Client.KLINE_INTERVAL_15MINUTE
    ticker = 'BTCUSDT'
    data = fetch_binance_data(ticker, "1 Jan 2023", "1 Jan 2024", interval)
    pattern = detect_head_shoulder(data)
    print(pattern)
