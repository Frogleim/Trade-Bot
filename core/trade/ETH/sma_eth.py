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
interval = '15m'
length = 20
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
closed = False


def calculate_bollinger_bands(interval, length, num_std_dev):
    klines = client.futures_klines(symbol='ETHUSDT', interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = df['close'].rolling(window=length).mean()
    df['std_dev'] = df['close'].rolling(window=length).std()
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])
    return df[['sma', 'upper_band', 'lower_band']].iloc[-1]


def check_sma():
    while True:
        bollinger_values = calculate_bollinger_bands(interval=config.interval, length=config.length, num_std_dev=config.num_std_dev)
        upper_band, lower_band = float(bollinger_values['upper_band']), float(bollinger_values['lower_band'])
        print(upper_band, lower_band)
        live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])
        logging.info(f'Price: {live_price} --- Upper Band: {upper_band}, Lower Band: {lower_band}')

        if live_price > upper_band + 4:
            logging.info(f'Live price above Upper Band. Simulating short position.')
            return 'Short', live_price
        elif live_price < lower_band - 4:
            logging.info(f'Live price below Lower Band. Simulating long position.')
            return 'Long', live_price
        else:
            continue


def trade():
    global closed
    signal, entry_price = check_sma()
    if signal == 'Long':
        iteration_count = 0
        try:
            position_handler.create_order(entry_price=entry_price,
                                          quantity=config.position_size,
                                          side='long')
        except Exception as e:
            print(e)
            position_handler.create_order(entry_price=entry_price,
                                          quantity=config.position_size,
                                          side='long')
        while True:
            iteration_count += 1
            res = tp_sl.pnl_long(entry_price, iteration_count)
            if res == 'Profit':
                logging.info(f'Closing Position with {res}')
                try:
                    position_handler.close_position(side='short', quantity=config.position_size)
                except Exception as e:
                    print(e)
                    position_handler.close_position(side='short', quantity=config.position_size)
                pnl_calculator.position_size()
                break
            elif res == 'Loss':
                logging.info(f'Closing Position with {res}')
                try:
                    position_handler.close_position(side='short', quantity=config.position_size)
                except Exception as e:
                    print(e)
                    position_handler.close_position(side='short', quantity=config.position_size)
                break

    if signal == 'Short':
        iteration_count = 0
        try:
            position_handler.create_order(entry_price=entry_price,
                                          quantity=config.position_size,
                                          side='short')
        except Exception as e:
            print(e)
            position_handler.create_order(entry_price=entry_price,
                                          quantity=config.position_size,
                                          side='short')
        while True:
            iteration_count += 1
            res = tp_sl.pnl_short(entry_price, iteration_count)
            if res == 'Profit':
                logging.info(f'Closing Position with {res}')
                try:
                    position_handler.close_position(side='long', quantity=config.position_size)
                except Exception as e:
                    print(e)
                    position_handler.close_position(side='long', quantity=config.position_size)
                pnl_calculator.position_size()
                break
            elif res == 'Loss':
                logging.info(f'Closing Position with {res}')
                try:
                    position_handler.close_position(side='long', quantity=config.position_size)
                except Exception as e:
                    print(e)
                    position_handler.close_position(side='long', quantity=config.position_size)
                break


if __name__ == '__main__':

    from send_email import send_email

    trades_count = 0
    while True:
        tp_sl.profit_checkpoint_list.clear()
        trades_count += 1
        trade()
        if trades_count == 8:
            send_email('Trades Successfully Finished',
                       'Trades Finished! Check your Binance account')
            break
