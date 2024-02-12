import asyncio
import time
from binance.client import AsyncClient
import pandas as pd
import logging_settings

active_trades = {}
symbols_list = ['XRPUSDT', 'ATOMUSDT', 'ADAUSDT', 'MATICUSDT']
stop_loss_levels = {}  # Dictionary to store stop-loss levels for each symbol
trailing_stop_distance = 0.02  # Example: 2% trailing stop distance


def clean_log_file():
    with open('./logs/finish_trade_log.log', 'w') as log_file:
        log_file.write('')


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


def get_current_price(client, symbol):
    current_price = client.futures_ticker(symbol=symbol)['lastPrice']
    return current_price


def read_alert(path=None):
    global data, is_empty
    with open('./logs/finish_trade_log.log', 'r') as alert_file:
        lines = alert_file.readlines()
        if lines:
            data = lines[0].strip().split(', ')  # Split the line into parts
            is_empty = True
        else:
            is_empty = False
    return is_empty, data


async def trigger(client, symbol, signal, close_price):
    global active_trades, symbols_list, stop_loss_levels
    if signal != 'Hold':
        active_trades[symbol] = True  # Mark symbol as actively trading
        stop_loss_levels[symbol] = close_price  # Record initial stop-loss level
        logging_settings.actions_logger.info(f'{symbol} {close_price} {signal}')
        symbols_list.remove(symbol)


async def check_trade_status():
    global symbols_list, is_empty, data
    is_empty, data = read_alert()
    if is_empty:
        cryptocurrency = data[0].split()[5]
        symbols_list.append(cryptocurrency)
        print(f'Trade for {cryptocurrency} was finished')


async def monitor_symbol(client, symbol, interval, length, num_std_dev):
    global active_trades, stop_loss_levels

    while True:
        if symbol not in active_trades:
            queue = asyncio.Queue()
            await get_bollinger_bands(client, symbol, interval, length, num_std_dev, queue)
            symbol, df = await queue.get()
            market_condition, close_price = await is_sideways_market(df, length)
            print('Checking trades status')
            print(f"Market condition for {symbol}: {market_condition}, Close Price: {close_price}")
            await check_trade_status()
            clean_log_file()
            await trigger(client, symbol, market_condition, close_price)
        else:
            # Check if the price has surpassed the highest price since triggering the sell order
            current_price = get_current_price(client, symbol)  # Example function to get current price
            if current_price > stop_loss_levels[symbol]:
                stop_loss_levels[symbol] = current_price * (1 - trailing_stop_distance)  # Update stop-loss level
        await asyncio.sleep(1)


async def monitor_symbols(client, symbols, interval, length, num_std_dev):
    symbol_tasks = []
    for symbol in symbols:
        task = asyncio.create_task(monitor_symbol(client, symbol, interval, length, num_std_dev))
        symbol_tasks.append(task)
    await asyncio.gather(*symbol_tasks)


async def main():
    global symbols_list
    client = await AsyncClient.create()
    interval = '3m'
    length = 20
    num_std_dev = 2
    await monitor_symbols(client, symbols_list, interval, length, num_std_dev)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

    clean_log_file()
