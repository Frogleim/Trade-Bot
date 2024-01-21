import logging
import sys
import pandas as pd
from binance.client import Client
import config
import pnl_calculator
import position_handler
import tp_sl

# Replace with your Binance API key and secret
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'

client = Client(api_key, api_secret)

symbol = 'BNBUSDT'
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

        if live_price > upper_band + 0.56:
            logging.info(f'Live price above Upper Band. Simulating short position.')
            return 'Short', live_price
        elif live_price < lower_band - 0.56:
            logging.info(f'Live price below Lower Band. Simulating long position.')
            return 'Long', live_price
        else:
            continue


def trade():
    global closed
    signal, entry_price, = check_sma()
    if signal == 'Buy':
        tp_sl.profit_checkpoint_list.clear()
        while True:
            res = tp_sl.pnl_long(entry_price)
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                pnl_calculator.position_size()
                break

    if signal == 'Sell':
        # Cleaning checkpoint list before trade
        tp_sl.profit_checkpoint_list.clear()

        while True:
            res = tp_sl.pnl_short(entry_price)
            if res == 'Profit' or res == 'Loss':
                logging.info(f'Closing Position with {res}')
                pnl_calculator.position_size()

                break


if __name__ == '__main__':
    while True:
        trade()
