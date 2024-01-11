
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

try:
    client = Client(api_key, api_secret)
except Exception as e:
    client = Client(api_key, api_secret)
    print(e)

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


def calculate_sma(symbol, interval, length):
    klines = client.futures_klines(symbol=config.trading_pair, interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = ta.sma(df['close'], length=length)
    return df['sma'].iloc[-1]


def check_sma():
    while True:
        sma_value = calculate_sma(config.trading_pair, interval, length)
        sma_up_side = sma_value + 1
        sma_down_side = sma_value - 1
        live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])
        logging.info(f'Price: {live_price} --- SMA: {sma_value}')
        if sma_up_side >= live_price >= sma_value:
            logging.info(f'Live price touches SMA from upside: {live_price}')
            return True, sma_up_side, sma_down_side, sma_value
        elif sma_down_side <= live_price <= sma_value:
            logging.info(f'Live price touches SMA from Down side: {live_price}')
            return False, sma_up_side, sma_down_side, sma_value
        else:
            continue


def break_point():
    is_open, sma_up, sma_down, sma = check_sma()

    while True:
        current_live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])
        print(f'Checking entry position')
        if is_open: # Touching from upside
            if current_live_price < sma_down - 1.5:
                logging.info(f'Live price went down by 2 points from SMA. Sell!')
                return 'Sell', current_live_price, sma
            if current_live_price > sma_up + 1.5:
                logging.info(f'Live price went down by 2 points from SMA. Sell!')
                return 'Buy', current_live_price, sma
        elif not is_open: # Touching from downside
            if current_live_price > sma_up + 1.5:
                logging.info(f'Live price went up by 2 points from SMA. Buy!')
                return 'Buy', current_live_price, sma
            if current_live_price < sma_down - 1.5:
                logging.info(f'Live price went down by 2 points from SMA. Sell!')
                return 'Sell', current_live_price, sma
        else:
            continue


def trade():
    global closed
    signal, entry_price, sma = break_point()
    if signal == 'Buy':
        tp_sl.profit_checkpoint_list.clear()

        while True:
            res = tp_sl.pnl_long(entry_price, sma)
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                pnl_calculator.position_size()
                break

    if signal == 'Sell':
        # Cleaning checkpoint list before trade
        tp_sl.profit_checkpoint_list.clear()
        while True:
            res = tp_sl.pnl_short(entry_price, sma)
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                pnl_calculator.position_size()
                break


if __name__ == '__main__':
    while True:
        trade()
