import logging
import os
import sys
from collections import Counter
from binance.client import Client
from . import config
import time
import logging_settings
from datetime import datetime

current_profit = 0
profit_checkpoint_list = []
current_checkpoint = 0.00
try:
    client = Client(config.API_KEY, config.API_SECRET)
except Exception as e:
    print(e)
    client = Client(config.API_KEY, config.API_SECRET)
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


def method_name_decorator(func):
    def wrapper(*args, **kwargs):
        logging.info(f'Executing method: {func.__name__}')
        return func(*args, **kwargs)

    return wrapper


def pnl_long(opened_price, entry_time):
    start_time = time.time()
    """
    Definition: Monitoring current position by profit checkpoint list
    Args:
        opened_price: Entry Price

    Returns: Profit or Loss signal as string


    """
    global current_profit, current_checkpoint, profit_checkpoint_list

    try:
        current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        orders = client.futures_position_information(symbol='MATICUSDT')
        pnl = float(orders[0]['unRealizedProfit']) * 1000
    except Exception as e:
        orders = client.futures_position_information(symbol='MATICUSDT')
        pnl = float(orders[0]['unRealizedProfit']) * 1000
        logging_settings.error_logs_logger.error(f'Error while monitoring current position: {e}--- Trying again...')
        current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']

    # logging_settings.system_log.info(
    #     f'Entry Price: {opened_price} --- Current Price: {current_price} --- Current Profit: {current_profit} ---'
    # )
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= pnl < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {pnl}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint} --> {pnl} --> Current Price {current_price}')

    if pnl < -80:
        return 'Loss'

    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (pnl < profit_checkpoint_list[-1] or pnl >= config.checkpoint_list[-1]
                and pnl > 0):

            body = \
                f'Position closed!.\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(current_price), 1)}\nProfit: {round(pnl, 1)}'
            logging.info(body)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


def pnl_short(opened_price, entry_time):
    start_time = time.time()
    """
    Definition: Monitoring current position by profit checkpoint list

    Args:
        opened_price: Entry Price

    Returns: Profit or Loss signals as string

    """
    global current_profit, current_checkpoint, profit_checkpoint_list

    try:
        current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        orders = client.futures_position_information(symbol='MATICUSDT')
        pnl = float(orders[0]['unRealizedProfit']) * 1000
    except Exception as e:
        orders = client.futures_position_information(symbol='MATICUSDT')
        pnl = float(orders[0]['unRealizedProfit']) * 1000
        logging_settings.error_logs_logger.error(f'Error while monitoring current position: {e}--- Trying again...')
        current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']

    if pnl < -80:
        return 'Loss'

    # logging_settings.system_log.info(
    #     f'Entry Price: {opened_price} --- Current Price: {current_price} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= pnl < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {pnl}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint} --> {pnl} --> Current Price {current_price}')
    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (pnl < profit_checkpoint_list[-1] or pnl >= config.checkpoint_list[-1]
                and pnl > 0):

            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(current_price), 1)}\nProfit: {round(pnl, 1)}'
            logging.info(body)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'
