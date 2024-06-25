import logging
import os
import sys
from collections import Counter
from binance.client import Client
from . import db

my_db = db.DataBase()
API_KEY, API_SECRET = my_db.get_binance_keys()
symbol, quantity, checkpoints, stop_loss = my_db.get_trade_coins()
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


def pnl_long(opened_price, indicator=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, stop_loss
    try:
        current_price = client.futures_ticker(symbol=symbol)['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=symbol)['lastPrice']

    current_profit = float(current_price) - float(opened_price)
    for i in range(len(checkpoints) - 1):
        if checkpoints[i] <= current_profit < checkpoints[i + 1]:
            if current_checkpoint != checkpoints[i]:  # Check if it's a new checkpoint
                current_checkpoint = checkpoints[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    if float(current_profit) <= -float(stop_loss):
        my_db.insert_test_trades(symbol=symbol, entry_price=opened_price, close_price='0.0',
                                 pnl=current_profit, indicator=indicator, is_profit=False)
        print('CLosing with lose')
        return 'Loss'
    logging.warning(
        f'Current checkpoint: --> {current_checkpoint} --> {current_profit} --> Current Price {current_price}')

    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (current_profit < profit_checkpoint_list[-1] or current_checkpoint >= checkpoints[-1]
                and current_profit > 0):
            body = \
                f'Position closed!.\nPosition data\nSymbol: {symbol}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            my_db.insert_test_trades(symbol=symbol, entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=True)

            return 'Profit'


def pnl_short(opened_price, indicator=None):
    global current_profit, current_checkpoint, profit_checkpoint_list
    try:
        current_price = client.futures_ticker(symbol=symbol)['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=symbol)['lastPrice']
    current_profit = float(opened_price) - float(current_price)
    for i in range(len(checkpoints) - 1):
        if checkpoints[i] <= current_profit < checkpoints[i + 1]:
            if current_checkpoint != checkpoints[i]:
                current_checkpoint = checkpoints[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    if float(current_profit) <= -float(stop_loss):
        my_db.insert_test_trades(symbol=symbol, entry_price=opened_price, close_price='0.0',
                                 pnl=current_profit, indicator=indicator, is_profit=False)
        print('CLosing with lose')
        return 'Loss'
    logging.warning(
        f'Current checkpoint: --> {current_checkpoint} --> {current_profit} --> Current Price {current_price}')
    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (current_profit < profit_checkpoint_list[-1] or current_checkpoint >= checkpoints[-1]
                and current_profit > 0):
            body = f'Position closed!\nPosition data\nSymbol: {symbol}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            my_db.insert_test_trades(symbol=symbol, entry_price=opened_price, close_price='0.0',
                                     pnl=current_profit, indicator=indicator, is_profit=True)

            return 'Profit'



if __name__ == '__main__':
    pnl_long(opened_price=0.554)