import asyncio
from binance.client import AsyncClient
import pandas as pd
import logging_settings
from xrp import xrp_trade
from atom import atom_trade
from matic import matic_trade
from ada import ada_trade


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
    elif symbol == 'MATICUSDT':
        result = await matic_trade.trade(signal=market_condition, entry_price=close_price)
    elif symbol == 'ADAUSDT':
        result = await ada_trade.trade(signal=market_condition, entry_price=close_price)
    else:
        result = None
    return result


async def monitor_symbol(client, symbol, interval, length, num_std_dev, symbol_status):
    while True:
        if symbol_status[symbol]:
            queue = asyncio.Queue()
            await get_bollinger_bands(client, symbol, interval, length, num_std_dev, queue)
            symbol, df = await queue.get()
            market_condition, close_price = await is_sideways_market(df, length)
            print(f"Market condition for {symbol}: {market_condition}, Close Price: {close_price}")

            if market_condition != 'Hold':
                symbol_status[symbol] = False  # Pause streaming for this symbol
                result = await execute_trade(client, symbol, market_condition, close_price)
                if result in ['Completed', 'Canceled', 'Timeout']:
                    symbol_status[symbol] = True  # Resume streaming if trade completed or canceled
                    continue
                symbol_status[symbol] = True  # Resume streaming after trade execution
        await asyncio.sleep(1)


async def monitor_symbols(client, symbols, interval, length, num_std_dev):
    symbol_tasks = []
    symbol_status = {symbol: True for symbol in symbols}  # Initialize status for each symbol as True (streaming ON)
    for symbol in symbols:
        task = asyncio.create_task(monitor_symbol(client, symbol, interval, length, num_std_dev, symbol_status))
        symbol_tasks.append(task)
    await asyncio.gather(*symbol_tasks)


async def main():
    client = await AsyncClient.create()
    symbols = ['XRPUSDT', 'ATOMUSDT', 'ADAUSDT', 'MATICUSDT']
    interval = '3m'
    length = 20
    num_std_dev = 2

    await monitor_symbols(client, symbols, interval, length, num_std_dev)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
