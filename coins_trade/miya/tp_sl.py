import logging
import os
import sys
from collections import Counter
from binance.client import Client
from . import db, fetch_sma

my_db = db.DataBase()
API_KEY, API_SECRET = my_db.get_binance_keys()
current_profit = 0
profit_checkpoint_list = []
current_checkpoint = 0.00
try:
    client = Client(API_KEY, API_SECRET)
except Exception as e:
    print(e)
    client = Client(API_KEY, API_SECRET)
price_history = []
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "coins_trade")
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


def pnl_long(opened_price, indicator):
    indicator_settings = my_db.get_trade_coins(indicator=indicator)

    global current_profit, current_checkpoint, profit_checkpoint_list, stop_loss
    try:
        current_price = client.futures_ticker(symbol=indicator_settings[1])['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=indicator_settings[1])['lastPrice']

    current_profit = float(current_price) - float(opened_price)
    for i in range(len(indicator_settings[3]) - 1):
        if indicator_settings[3][i] <= current_profit < indicator_settings[3][i + 1]:
            if current_checkpoint != indicator_settings[3][i]:  # Check if it's a new checkpoint
                current_checkpoint = indicator_settings[3][i] * 1.15
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if indicator == 'EMA':
        sma = fetch_sma.get_ema()
        if float(current_profit) <= float(sma):
            my_db.insert_test_trades(symbol=indicator_settings[3], entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=False)
            print('CLosing with lose')
            return 'Loss'
    else:
        if float(current_profit) <= -float(indicator_settings[4]):
            my_db.insert_test_trades(symbol=indicator_settings[3], entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=False)
            print('CLosing with lose')
            return 'Loss'
    logging.warning(
        f'Current checkpoint: --> {current_checkpoint} --> {current_profit} --> Current Price {current_price}')

    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (current_profit < profit_checkpoint_list[-1] or current_checkpoint >= indicator_settings[3][-1]
                and current_profit > 0):
            body = \
                f'Position closed!.\nPosition data\nSymbol: {indicator_settings[1]}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            my_db.insert_test_trades(symbol=indicator_settings[1], entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=True)

            return 'Profit'


def pnl_short(opened_price, indicator):
    indicator_settings = my_db.get_trade_coins(indicator=indicator)

    global current_profit, current_checkpoint, profit_checkpoint_list
    try:
        current_price = client.futures_ticker(symbol=indicator_settings[1])['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=indicator_settings[1])['lastPrice']
    current_profit = float(opened_price) - float(current_price)
    for i in range(len(indicator_settings[3]) - 1):
        if indicator_settings[3][i] <= current_profit < indicator_settings[3][i + 1]:
            if current_checkpoint != indicator_settings[3][i]:
                current_checkpoint = indicator_settings[3][i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if indicator == 'EMA':
        sma = fetch_sma.get_ema()
        if float(current_price) >= float(sma):
            my_db.insert_test_trades(symbol=indicator_settings[1], entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=False)
            print('CLosing with lose')
            return 'Loss'
    else:
        if float(current_profit) <= -float(indicator_settings[4]):
            my_db.insert_test_trades(symbol=indicator_settings[1], entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=False)
            print('CLosing with lose')
            return 'Loss'
    logging.warning(
        f'Current checkpoint: --> {current_checkpoint} --> {current_profit} --> Current Price {current_price}')
    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (current_profit < profit_checkpoint_list[-1] or current_checkpoint >= indicator_settings[3][-1]
                and current_profit > 0):
            body = f'Position closed!\nPosition data\nSymbol: {indicator_settings[1]}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            my_db.insert_test_trades(symbol=indicator_settings[1], entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=True)

            return 'Profit'



if __name__ == '__main__':
    pnl_long(opened_price=0.554)