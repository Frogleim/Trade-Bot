import warnings

warnings.filterwarnings(action='ignore')
import pandas as pd
import logging, asyncio, aiohttp
from binance.client import Client
from coins_trade.miya import logging_settings
from db import DataBase

# Binance API setup
my_db = DataBase()
api_key, api_secret = my_db.get_binance_keys()
client = Client(api_key, api_secret)

interval = '15m'  # Use '15m' for 15-minute intervals
length = 21
num_std_dev = 2


async def fetch_klines(session, symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f'Error fetching klines: {e}')
        return []


async def calculate_bollinger_bands(session, interval, length, num_std_dev):
    klines = await fetch_klines(session, 'MATICUSDT', interval)
    if not klines or len(klines) < length:
        return pd.Series([None, None, None, None], index=['sma', 'upper_band', 'lower_band', 'previous_close'])

    close_prices = [float(kline[4]) for kline in klines]
    previous_close = close_prices[-2] if len(close_prices) >= 2 else None

    df = pd.DataFrame({'close': close_prices})
    df['sma'] = df['close'].rolling(window=length).mean()
    df['std_dev'] = df['close'].rolling(window=length).std()
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])

    result = df[['sma', 'upper_band', 'lower_band']].iloc[-1]
    result['previous_close'] = previous_close
    return result


async def check_sma():
    async with aiohttp.ClientSession() as session:
        bollinger_values = await calculate_bollinger_bands(session, interval=interval, length=length,
                                                           num_std_dev=num_std_dev)
        upper_band, lower_band = float(bollinger_values['upper_band']), float(bollinger_values['lower_band'])
        previous_close = bollinger_values['previous_close']

        logging.info(f'Bollinger Bands - Upper: {upper_band}, Lower: {lower_band}')

        logging_settings.system_log.info(
            f'Price: {previous_close} --- Upper Band: {upper_band}, Lower Band: {lower_band}')

        if previous_close is None:
            return 'Hold', previous_close

        if previous_close > upper_band + 0.0003:
            return 'Sell', previous_close
        elif previous_close < lower_band - 0.0003:
            return 'Buy', previous_close
        else:
            return 'Hold', previous_close


# Running the asynchronous function
async def main():
    result = await check_sma()
    return result


if __name__ == '__main__':
    res = asyncio.run(main())
    print(res)
