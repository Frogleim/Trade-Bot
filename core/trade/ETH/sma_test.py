import time

import pandas as pd
import pandas_ta as ta
from binance.client import Client
import tp_sl, config, pnl_calculator, position_handler
import os
import logging
import sys

# Replace with your Binance API key and secret
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'

client = Client(api_key, api_secret)
interval = '15m'  # Use '15m' for 15-minute intervals
length = 20
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

closed = False


def calculate_bollinger_bands(interval, length, num_std_dev):
    klines = client.futures_klines(symbol='ETHUSDT', interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})

    # Calculate SMA using pandas
    df['sma'] = df['close'].rolling(window=length).mean()

    # Calculate standard deviation
    df['std_dev'] = df['close'].rolling(window=length).std()

    # Calculate upper and lower Bollinger Bands
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])

    return df[['sma', 'upper_band', 'lower_band']].iloc[-1]


def check_sma():
    while True:
        bollinger_values = calculate_bollinger_bands(config.trading_pair, interval, length)
        upper_band, lower_band = bollinger_values['upper_band'], bollinger_values['lower_band']
        live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])
        logging.info(f'Price: {live_price} --- Upper Band: {upper_band}, Lower Band: {lower_band}')

        if live_price > upper_band:
            logging.info(f'Live price above Upper Band. Simulating short position.')
            return 'Short', upper_band, lower_band
        elif live_price < lower_band:
            logging.info(f'Live price below Lower Band. Simulating long position.')
            return 'Long', upper_band, lower_band
        else:
            continue


def trade():
    global closed
    signal, entry_price, sma = check_sma()
    if signal == 'Buy':
        iteration_count = 0

        tp_sl.profit_checkpoint_list.clear()
        while True:
            iteration_count += 1
            res = tp_sl.pnl_long(entry_price, iteration_count)
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                break

    if signal == 'Sell':
        iteration_count = 0
        # Cleaning checkpoint list before trade
        tp_sl.profit_checkpoint_list.clear()
        while True:
            iteration_count += 1

            res = tp_sl.pnl_short(entry_price, iteration_count)
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                break
            time.sleep(0.5)


if __name__ == '__main__':
    while True:
        trade()
