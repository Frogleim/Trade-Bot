import logging
import os
import sys
from collections import Counter
from binance.client import Client
from . import config, db
import time
import logging_settings


current_profit = 0
profit_checkpoint_list = []
current_checkpoint = None
try:
    client = Client(config.API_KEY, config.API_SECRET)
except Exception as e:
    print(e)
    client = Client(config.API_KEY, config.API_SECRET)
price_history = []
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "bot")
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


def pnl_long(opened_price):
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
    except Exception as e:
        logging_settings.error_logs_logger.error(f'Error while monitoring current position: {e}--- Trying again...')
        current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']

    current_profit = float(current_price) - float(opened_price)
    logging.info(
        f'Entry Price: {opened_price} --- Current Price: {current_price} --- Current Profit: {current_profit} ---'
    )
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint} --> {current_profit}')

    if len(profit_checkpoint_list) >= 0 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if current_profit < profit_checkpoint_list[-1] or current_checkpoint >= config.checkpoint_list[-1]:
            total_time = time.time() - start_time
            connect_base = db.DataBase()
            connect_base.insert_trades(
                symbol=config.trading_pair,
                entry_price=opened_price,
                close_price=current_price,
                pnl=current_price - opened_price,
                side='long',
                time_in_trade=total_time
            )
            body = \
                f'Position closed!.\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


def pnl_short(opened_price):
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
    except Exception as e:
        logging_settings.error_logs_logger.error(f'Error while monitoring current position: {e} --- Trying again...')
        current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']

    current_profit = float(opened_price) - float(current_price)
    logging.info(
        f'Entry Price: {opened_price} --- Current Price: {current_price} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint} --> {current_profit}')
    if len(profit_checkpoint_list) >= 0 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if current_profit < profit_checkpoint_list[-1] or current_checkpoint >= config.checkpoint_list[-1]:
            total_time = time.time() - start_time
            connect_base = db.DataBase()
            connect_base.insert_trades(
                symbol=config.trading_pair,
                entry_price=opened_price,
                close_price=current_price,
                pnl=opened_price - current_price,
                side='short',
                time_in_trade=total_time

            )
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'
