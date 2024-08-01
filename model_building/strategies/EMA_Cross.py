import time
import pandas as pd
import numpy as np
from binance.client import Client
import aiohttp
import asyncio
import logging
import ta
import logging_settings
import ccxt.async_support as ccxt_async

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 5
long_period = 8
adx_period = 14
symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 month ago UTC'
atr_period = 14

async def fetch_ohlcv(symbol='MATIC/USDT', timeframe="15m", limit=1000):
    exchange = ccxt_async.binance()
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    await exchange.close()
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

async def calculate_indicators():
    try:
        df = await fetch_ohlcv()
        
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        if df.empty:
            logging_settings.error_logs_logger.error('DataFrame is empty after fetching data')
            return df

        # Calculate ADX
        df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)


        # Calculate EMAs
        df['EMA_Short'] = df['close'].ewm(span=short_period, adjust=False).mean()
        df['EMA_Long'] = df['close'].ewm(span=long_period, adjust=False).mean()

        df.dropna(inplace=True)

        if df.empty:
            logging_settings.error_logs_logger.error('DataFrame is empty after calculations')
        
        return df
    except Exception as e:
        logging_settings.error_logs_logger.error(f'Error in calculate_indicators: {e}')
        return pd.DataFrame()

async def check_signal():
    data = await calculate_indicators()
    if data.empty:
        logging_settings.error_logs_logger.error('No data available for signal check')
        return 'No Data', None

    data['Signal'] = 0
    data['Signal'] = np.where((data['EMA_Short'] > data['EMA_Long']) & (data['ADX'] > 25), 1,
                              np.where((data['EMA_Short'] < data['EMA_Long']) & (data['ADX'] > 25), -1, 0))

    data['Crossover'] = data['Signal'].diff()
    print(data['Crossover'].iloc[-1])

    last_close_price = data['close'].iloc[-1]
    short_ema = data["EMA_Short"].iloc[-1]
    long_ema = data["EMA_Long"].iloc[-1]
    atr = data['ATR'].iloc[-1]

    if short_ema > long_ema:
        logging_settings.system_log.warning("Waiting for downtrend!")
        while True:
            data = await calculate_indicators()
            if data.empty:
                logging_settings.error_logs_logger.error('No data available during downtrend wait')
                continue
            print(atr)
            short_ema = data["EMA_Short"].iloc[-1]
            long_ema = data["EMA_Long"].iloc[-1]
            last_close_price = data['close'].iloc[-1]
            is_time = True if atr > 0.0026 else False 
            print(is_time)

            logging_settings.system_log.warning('EMA has not crossed yet')
            if short_ema < long_ema:
                logging_settings.system_log.warning('EMA crosses')
                if last_close_price < long_ema and is_time:
                    logging_settings.system_log.warning(f'EMA crosses!\nShort EMA: {short_ema}, Long EMA: {long_ema} ADX: {data["ADX"].iloc[-1]} ATR: {atr} Signal: Buy')
                    return 'Sell', last_close_price

    elif short_ema < long_ema:
        logging_settings.system_log.warning("Waiting for uptrend!")
        while True:
            data = await calculate_indicators()
            if data.empty:
                logging_settings.error_logs_logger.error('No data available during uptrend wait')
                continue
            
            short_ema = data["EMA_Short"].iloc[-1]
            long_ema = data["EMA_Long"].iloc[-1]
            last_close_price = data['close'].iloc[-1]
            is_time = True if atr > 0.0026 else False
            print(atr)
            print(is_time)
            logging_settings.system_log.warning('EMA has not crossed yet')
            if short_ema > long_ema:
                if last_close_price > long_ema and is_time:
                    logging_settings.system_log.warning(f'EMA crosses!\nShort EMA: {short_ema}, Long EMA: {long_ema} ADX: {data["ADX"].iloc[-1]} ATR: {atr} Signal: Buy')
                    return "Buy", last_close_price

    else:
        return 'Hold', last_close_price

async def main():
    try:
        while True:
            result = await check_signal()
            print(result)
    except Exception as e:
        logging_settings.error_logs_logger.error(f'EMA Crossover script down!\nError message: {e}')


if __name__ == '__main__':
    asyncio.run(main())
