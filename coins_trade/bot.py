import time
import strategy
import logging_settings
from binance.client import Client
import json
import os
from strategies import sma

client = Client()

base_dir = os.path.dirname(os.path.abspath(__file__))
files_dir = os.path.join(base_dir, r"miya")
symbols_list = ['XRPUSDT', 'ATOMUSDT', 'ADAUSDT', 'MATICUSDT']
not_trading_symbols_list = ['XRPUSDT', 'ATOMUSDT', 'ADAUSDT', 'MATICUSDT']
symbol = 'MATICUSDT'
interval = '1h'
lookback = '30 day'
short_window = 7  # Short term SMA window
long_window = 25  # Long term SMA window

def read_config_json():
    logging_settings.system_logs_logger.info('Reading config file')
    with open(f'{base_dir}/config.json', 'r') as f:
        data = json.load(f)
    return data


def rewrite_config_json(data):
    logging_settings.system_logs_logger.info('Rewriting config file')
    with open('config.json', 'w') as f:
        pass


def clean_log_file():
    logging_settings.system_logs_logger.info('Cleaning log file.')
    with open('./logs/finish_trade_log.log', 'w') as log_file:
        log_file.write('')


def process_symbol(symbol):
    logging_settings.system_logs_logger.info(f'Processing symbol {symbol}')
    df = strategy.get_latest_candlestick(symbol[0]['symbol'])
    signal, price = sma.execute_strategy(symbol=symbol[0]['symbol'],
                                            interval=interval, lookback=lookback,
                                            short_window=short_window, long_window=long_window)

    if symbol[0]['symbol'] in not_trading_symbols_list:
        while True:
            logging_settings.system_logs_logger.info(f'{symbol[0]["symbol"]} Hold')
            if signal != 'Hold':
                logging_settings.system_logs_logger.info(f'{symbol[0]["symbol"]} is not Hold')

                break
            time.sleep(500)
        signal = signal
        logging_settings.actions_logger.info(
            f'{symbol[0]["symbol"]} {price} {signal} {symbol[0]["position_size"]}')


def check_trade_status():
    global symbols_list
    while True:
        with open('./logs/finish_trade_log.log', 'r') as alert_file:
            lines = alert_file.readlines()
            if lines:
                data = lines[0].strip().split(', ')  # Split the line into parts
                cryptocurrency = data[0].split()[5]
                symbols_list.append(cryptocurrency)
                logging_settings.system_logs_logger.info(f'Trade for {cryptocurrency} was finished')
                return True, cryptocurrency


def run():
    logging_settings.system_logs_logger.info('Bot started')
    while True:
        logging_settings.system_logs_logger.info('Waiting for price signals...')
        symbols = read_config_json()
        process_symbol(symbols["cryptocurrency"])
        logging_settings.system_logs_logger.info('Waiting for trade finished...')
        is_finished, cryptocurrency = check_trade_status()
        logging_settings.system_logs_logger.info(f'Finished trade for symbol {cryptocurrency}')
        if is_finished:
            clean_log_file()
            not_trading_symbols_list.append(cryptocurrency)
            time.sleep(1800)


if __name__ == '__main__':
    run()
