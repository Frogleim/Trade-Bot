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


def calculate_sma(interval, length):
    klines = client.futures_klines(symbol=config.trading_pair, interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = ta.sma(df['close'], length=length)
    return df['sma'].iloc[-1]


def check_sma():
    while True:
        sma_value = calculate_sma(interval, length)
        sma_up_side = sma_value + 1
        sma_down_side = sma_value - 1
        live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])
        logging.info(f'Price: {live_price} --- SMA: {sma_value}')
        if sma_down_side <= live_price <= sma_up_side:
            logging.info(f'Live price touches SMA: {live_price}')
            return True, sma_up_side, sma_down_side, sma_value
        else:
            continue


def break_point():
    is_open, sma_up, sma_down, sma = check_sma()

    while True:
        current_live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])
        print(f'Checking entry position')
        if current_live_price <= sma_down:
            logging.info(f'Live price went down by 4 points from SMA. Sell!')
            return 'Sell', current_live_price, sma
        elif current_live_price >= sma_up:
            logging.info(f'Live price went up by 4 points from SMA. Buy!')
            return 'Buy', current_live_price, sma
        else:
            continue


def trade():
    global closed
    signal, entry_price, sma = break_point()
    if signal == 'Buy':
        iteration_count = 0

        tp_sl.profit_checkpoint_list.clear()
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
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                try:
                    position_handler.close_position(side='short', quantity=config.position_size)
                except Exception as e:
                    print(e)
                    position_handler.close_position(side='short', quantity=config.position_size)
                # pnl_calculator.position_size()

                break

    if signal == 'Sell':
        iteration_count = 0

        # Cleaning checkpoint list before trade
        tp_sl.profit_checkpoint_list.clear()
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
            if res == 'Profit' or res == 'Loss':

                logging.info(f'Closing Position with {res}')
                try:
                    position_handler.close_position(side='long', quantity=config.position_size)
                except Exception as e:
                    print(e)
                    position_handler.close_position(side='long', quantity=config.position_size)
                # pnl_calculator.position_size()

                break


if __name__ == '__main__':
    while True:
        trade()
