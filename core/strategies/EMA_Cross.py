import warnings
import time
import pandas as pd
import numpy as np
from binance.client import Client
import aiohttp
import asyncio
import logging
import ta
from . import logging_settings
import ccxt.async_support as ccxt_async

warnings.filterwarnings(action='ignore')

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 5
long_period = 8
adx_period = 14
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 month ago UTC'
atr_period = 14

symbols = ['MATIC/USDT', 'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT']

async def fetch_ohlcv(symbol, timeframe="15m", limit=1000):
    exchange = ccxt_async.binance()
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    await exchange.close()
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

async def calculate_indicators(symbol):
    try:
        df = await fetch_ohlcv(symbol)
        
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        if df.empty:
            logging_settings.error_logs_logger.error(f'DataFrame is empty after fetching data for {symbol}')
            return df

        # Calculate ADX
        df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)
        df['sar'] = ta.trend.PSARIndicator(high=df['high'], low=df['low'], close=df['close']).psar()
        
        # Calculate rolling highs and lows to identify support and resistance
        df['High_Rolling'] = df['high'].rolling(window=20).max()
        df['Low_Rolling'] = df['low'].rolling(window=20).min()

        df['Support'] = df['Low_Rolling'].shift(1)
        df['Resistance'] = df['High_Rolling'].shift(1)
        # Calculate EMAs
        df['EMA_Short'] = df['close'].ewm(span=short_period, adjust=False).mean()
        df['EMA_Long'] = df['close'].ewm(span=long_period, adjust=False).mean()

        df.dropna(inplace=True)

        if df.empty:
            logging_settings.error_logs_logger.error(f'DataFrame is empty after calculations for {symbol}')
        
        return df
    except Exception as e:
        logging_settings.error_logs_logger.error(f'Error in calculate_indicators for {symbol}: {e}')
        return pd.DataFrame()

async def check_signal(symbol):
    data = await calculate_indicators(symbol)
    if data.empty:
        logging_settings.error_logs_logger.error(f'No data available for signal check for {symbol}')
        return symbol, 'No Data', None

    data['Signal'] = 0
    data['Signal'] = np.where((data['EMA_Short'] > data['EMA_Long']) & (data['ADX'] > 25), 1,
                              np.where((data['EMA_Short'] < data['EMA_Long']) & (data['ADX'] > 25), -1, 0))

    data['Crossover'] = data['Signal'].diff()

    last_close_price = data['close'].iloc[-1]
    short_ema = data["EMA_Short"].iloc[-1]
    long_ema = data["EMA_Long"].iloc[-1]
    atr = data['ATR'].iloc[-1]
    adx = data['ADX'].iloc[-1]
    sar = data['sar'].iloc[-1]
    if short_ema > long_ema:
        logging_settings.system_log.warning(f"Waiting for downtrend for {symbol}!")
        while True:
            data = await calculate_indicators(symbol)
            if data.empty:
                logging_settings.error_logs_logger.error(f'No data available during downtrend wait for {symbol}')
                continue
            short_ema = data["EMA_Short"].iloc[-1]
            long_ema = data["EMA_Long"].iloc[-1]
            last_close_price = data['close'].iloc[-1]
            is_adx = True if adx > 22 else False
            is_sar = True if sar > short_ema else False 

            print(f'{symbol} Long ema: {long_ema} Short ema: {short_ema} ADX: {is_adx} SAR: {sar} is SAR: {is_sar}')

            logging_settings.system_log.warning(f'EMA has not crossed yet for {symbol}')
            if short_ema < long_ema:
                logging_settings.system_log.warning(f'EMA crosses for {symbol}')
                if last_close_price < long_ema and is_adx and is_sar:
                    logging_settings.system_log.warning(f'{symbol} EMA crosses!\nShort EMA: {short_ema}, Long EMA: {long_ema} ADX: {data["ADX"].iloc[-1]} ATR: {atr} Signal: Buy')
                    return symbol, 'Sell', last_close_price
            return symbol, 'Hold', last_close_price


    elif short_ema < long_ema:
        logging_settings.system_log.warning(f"Waiting for uptrend for {symbol}!")
        while True:
            data = await calculate_indicators(symbol)
            if data.empty:
                logging_settings.error_logs_logger.error(f'No data available during uptrend wait for {symbol}')
                continue
            
            short_ema = data["EMA_Short"].iloc[-1]
            long_ema = data["EMA_Long"].iloc[-1]
            last_close_price = data['close'].iloc[-1]
            is_sar = True if sar < short_ema else False 
            is_adx = True if adx > 22 else False
            print(f'{symbol} Long ema: {long_ema} Short ema: {short_ema} ADX: {is_adx} SAR: {sar} is SAR: {is_sar}')
            logging_settings.system_log.warning(f'EMA has not crossed yet for {symbol}')
            if short_ema > long_ema:
                if last_close_price > long_ema and is_adx and is_sar:
                    logging_settings.system_log.warning(f'{symbol} EMA crosses!\nShort EMA: {short_ema}, Long EMA: {long_ema} ADX: {data["ADX"].iloc[-1]} ATR: {atr} Signal: Buy')
                    return symbol, "Buy", last_close_price
            print('No signal ')
            return symbol, 'Hold', last_close_price


    else:
        return symbol, 'Hold', last_close_price

async def main():
    try:
        tasks = [check_signal(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result)
    except Exception as e:
        logging_settings.error_logs_logger.error(f'EMA Crossover script down!\nError message: {e}')

if __name__ == '__main__':
    asyncio.run(main())
