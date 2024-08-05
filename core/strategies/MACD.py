import warnings
warnings.simplefilter(action='ignore')


import pandas as pd
import ccxt.async_support as ccxt
import numpy as np
import asyncio


async def fetch_ohlcv(symbol='MATIC/USDT', timeframe='15m', limit=100):
    exchange = ccxt.binance()
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    await exchange.close()
    return df


def generate_signals(df):
    ma1 = 12
    ma2 = 26
    signals = df.copy()
    signals['ma1'] = signals['close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['close'].rolling(window=ma2, min_periods=1, center=False).mean()
    signals['positions'] = 0
    signals['positions'][ma1:] = np.where(signals['ma1'][ma1:] >= signals['ma2'][ma1:], 1, 0)
    signals['signals'] = signals['positions'].diff()

    # Map numeric signals to string signals
    signal_map = {
        1.0: 'Buy',
        -1.0: 'Sell',
        0.0: 'Hold'
    }
    signals['signals'] = signals['signals'].map(signal_map)

    signals['oscillator'] = signals['ma1'] - signals['ma2']
    return signals


async def main():
    df = await fetch_ohlcv()
    signals = generate_signals(df)


if __name__ == '__main__':
    asyncio.run(main())
