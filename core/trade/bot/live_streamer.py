import asyncio
from binance.client import AsyncClient
import pandas as pd
import logging_settings
from xrp import xrp_trade
from bnb import bnb_trade
from atom import atom_trade

async def is_sideways_market(data, num_periods):
    bollinger_values = data.iloc[-num_periods:][['upper_band', 'lower_band', 'close']]
    upper_band, lower_band = bollinger_values['upper_band'].iloc[-1], bollinger_values['lower_band'].iloc[-1]
    close_price = bollinger_values['close'].iloc[-2]
    print(f'Lower Band: {lower_band} --> Upper Band: {upper_band} --> Close Price: {close_price}')
    if close_price < lower_band:
        return 'Long', close_price
    elif close_price > upper_band:
        return 'Short', close_price
    else:
        return 'Hold', close_price

async def get_bollinger_bands(client, symbol, interval, length, num_std_dev, queue):
    try:
        klines = await client.futures_klines(symbol=symbol, interval=interval)
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        klines = await client.futures_klines(symbol=symbol, interval=interval)

    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = df['close'].rolling(window=length).mean()
    df['std_dev'] = df['close'].rolling(window=length).std()
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])
    await queue.put((symbol, df))

async def execute_trade(client, symbol, market_condition, close_price):
    if symbol == 'XRPUSDT':
        result = await xrp_trade.trade(signal=market_condition, entry_price=close_price)
    elif symbol == 'ATOMUSDT':
        result = await atom_trade.trade(signal=market_condition, entry_price=close_price)
    elif symbol == 'BNBUSDT':
        result = await bnb_trade.trade(signal=market_condition, entry_price=close_price)
    else:
        result = None
    return result

async def monitor_symbols(client, symbols, interval, length, num_std_dev):
    while True:
        for symbol in symbols:
            queue = asyncio.Queue()
            await get_bollinger_bands(client, symbol, interval, length, num_std_dev, queue)
            symbol, df = await queue.get()
            market_condition, close_price = await is_sideways_market(df, length)
            print(f"Market condition for {symbol}: {market_condition}, Close Price: {close_price}")

            if market_condition != 'Hold':
                result = await execute_trade(client, symbol, market_condition, close_price)
                if result in ['Completed', 'Canceled', 'Timeout']:
                    continue
        await asyncio.sleep(1)

async def main():
    client = await AsyncClient.create()
    symbols = ['XRPUSDT', 'ATOMUSDT', 'BNBUSDT']
    interval = '3m'
    length = 20
    num_std_dev = 2

    await monitor_symbols(client, symbols, interval, length, num_std_dev)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
