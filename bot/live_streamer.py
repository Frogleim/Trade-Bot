import asyncio
from binance.client import AsyncClient
import pandas as pd

from bot import logging_settings

active_trades = {}
symbols_list = ['XRPUSDT', 'ATOMUSDT', 'ADAUSDT', 'MATICUSDT']
stop_loss_levels = {}  # Dictionary to store stop-loss levels for each symbol
trailing_stop_distance = 0.02  # Example: 2% trailing stop distance
volume_threshold = 1.5  # Current volume should be 1.5 times greater than average volume

async def clean_log_file():
    with open('./logs/finish_trade_log.log', 'w') as log_file:
        log_file.write('')

def generate_signals(data, short_window=50, long_window=200):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0

    # Calculate the moving averages
    signals['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1).mean()

    # Generate buy signals
    signals.loc[signals['short_mavg'] > signals['long_mavg'], 'signal'] = 1

    # Generate sell signals
    signals.loc[signals['short_mavg'] < signals['long_mavg'], 'signal'] = -1

    return signals

async def get_current_price(client, symbol):
    current_price = await client.futures_ticker(symbol=symbol)['lastPrice']
    return current_price

async def analyze_volume(client, symbol, interval, volume_threshold):
    try:
        klines = await client.futures_klines(symbol=symbol, interval=interval)
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        klines = await client.futures_klines(symbol=symbol, interval=interval)

    volumes = [float(kline[5]) for kline in klines]
    average_volume = sum(volumes) / len(volumes)
    current_volume = volumes[-1]

    if current_volume > average_volume * volume_threshold:
        return True  # Volume confirmation
    else:
        return False

async def trigger(client, symbol, signal, close_price):
    global active_trades, symbols_list, stop_loss_levels
    if signal != 'Hold':
        active_trades[symbol] = True  # Mark symbol as actively trading
        stop_loss_levels[symbol] = close_price  # Record initial stop-loss level
        logging_settings.actions_logger.info(f'{symbol} {close_price} {signal}')
        symbols_list.remove(symbol)

async def check_trade_status():
    global symbols_list, data
    with open('./logs/finish_trade_log.log', 'r') as alert_file:
        lines = alert_file.readlines()
        if lines:
            data = lines[0].strip().split(', ')  # Split the line into parts
            cryptocurrency = data[0].split()[5]
            symbols_list.append(cryptocurrency)
            print(f'Trade for {cryptocurrency} was finished')
            await clean_log_file()


async def monitor_symbol(client, symbol, interval, short_window, long_window, volume_threshold):
    global active_trades, stop_loss_levels

    while True:
        if symbol not in active_trades:
            try:
                klines = await client.futures_klines(symbol=symbol, interval=interval)
            except Exception as e:
                logging_settings.error_logs_logger.error(e)
                klines = await client.futures_klines(symbol=symbol, interval=interval)

            close_prices = [float(kline[4]) for kline in klines]
            df = pd.DataFrame({'close': close_prices})
            signals = generate_signals(df, short_window, long_window)
            last_signal = signals['signal'].iloc[-1]
            last_close_price = close_prices[-1]

            if last_signal == 1:
                await check_trade_status()  # Check if trade was finished
                await trigger(client, symbol, 'Long', last_close_price)

            elif last_signal == -1:
                await check_trade_status()  # Check if trade was finished
                await trigger(client, symbol, 'Short', last_close_price)
            else:
                await asyncio.sleep(60)  # Wait for a minute and check again
                continue



async def monitor_symbols(client, symbols, interval, short_window, long_window, volume_threshold):
    symbol_tasks = []
    for symbol in symbols:
        task = asyncio.create_task(monitor_symbol(client, symbol, interval, short_window, long_window, volume_threshold))
        symbol_tasks.append(task)
    await asyncio.gather(*symbol_tasks)

async def main():
    global symbols_list
    client = await AsyncClient.create()
    interval = '3m'
    short_window = 50
    long_window = 200
    await monitor_symbols(client, symbols_list, interval, short_window, long_window, volume_threshold)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
