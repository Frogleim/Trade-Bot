import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import ccxt.async_support as ccxt_async

since = ccxt.binance().parse8601('2023-01-01T00:00:00Z')


async def fetch_ohlcv(symbol='MATIC/USDT', timeframe="15m", limit=1000):
    exchange = ccxt_async.binance()
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    await exchange.close()
    return df


def dual_thrust_strategy(df, k1=0.5, k2=0.5, lookback=5):
    df['range1'] = df['high'].rolling(lookback).max() - df['close'].rolling(lookback).min()
    df['range2'] = df['close'].rolling(lookback).max() - df['low'].rolling(lookback).min()
    df['range'] = df[['range1', 'range2']].max(axis=1)

    df['buy_trigger'] = df['open'] + k1 * df['range']
    df['sell_trigger'] = df['open'] - k2 * df['range']

    signal_map = {
        1.0: 'Buy',
        -1.0: 'Sell',
        0.0: 'Hold'
    }

    df['signal'] = np.where(df['close'] > df['buy_trigger'], 1, np.where(df['close'] < df['sell_trigger'], -1, 0))
    df['signal'] = df['signal'].map(signal_map)
    return df




