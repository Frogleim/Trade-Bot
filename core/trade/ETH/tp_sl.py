import logging
import os
import random
import sys
from collections import Counter
from binance.client import Client
import config
import files_manager

current_profit = 0
profit_checkpoint_list = []
current_checkpoint = None
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
try:
    client = Client(api_key, api_secret)
except Exception as e:
    print(e)
    client = Client(api_key, api_secret)
price_history = []
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "ETH")
print(files_dir)
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


@method_name_decorator
def pnl_long(opened_price, iteration_count):
    """
    Definition: Monitoring current position by profit checkpoint list
    Args:
        iteration_count:
        opened_price: Entry Price

    Returns: Profit or Loss signal as string


    """
    global current_profit, current_checkpoint, profit_checkpoint_list
    iteration_count += 1  # Set iteration counter
    current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(current_price) - float(opened_price)
    logging.info(
        f'Entry Price: {opened_price} --- Current Price: {current_price} --- Current Profit: {current_profit} ---'
        f'Iteration: {iteration_count}')
    for i in range(len(config.checkpoint_list_scalping) - 1):
        if config.checkpoint_list_scalping[i] <= current_profit < config.checkpoint_list_scalping[i + 1]:
            if current_checkpoint != config.checkpoint_list_scalping[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list_scalping[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    stop_loss = float(opened_price) + config.SL  # Set up Stop Loss
    if float(current_price) >= stop_loss:
        logging.info('Break even price was passed!')
        files_manager.insert_scalping_data(opened_price, current_price, current_profit)
        if iteration_count >= 7000 and len(profit_checkpoint_list) == 0:
            return 'Loss'
    logging.warning(f'Current checkpoint: --> {current_checkpoint}')

    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[
        -2] is not None and iteration_count >= random.randint(2000, 5000):
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if current_profit < profit_checkpoint_list[-2] or current_checkpoint >= config.checkpoint_list_scalping[-1]:
            body = \
                f'Position closed!.\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            position_size = config.position_size
            save_data = (position_size * float(current_price)) / 100
            files_manager.insert_scalping_data(opened_price, current_price, current_profit, round(save_data, 3),
                                               iteration_count)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')

            return 'Profit'

    if len(profit_checkpoint_list) > 0 and current_profit <= profit_checkpoint_list[0]:
        body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        position_size = config.position_size
        save_data = (position_size * float(current_price)) / 100
        files_manager.insert_scalping_data(opened_price, current_price, current_profit, round(save_data, 3),
                                           iteration_count)
        logging.info('Saving data')
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
        return 'Profit'


@method_name_decorator
def pnl_short(opened_price, iteration_count):
    """
    Definition: Monitoring current position by profit checkpoint list

    Args:
        iteration_count:
        opened_price: Entry Price

    Returns: Profit or Loss signals as string

    """
    global current_profit, current_checkpoint, profit_checkpoint_list

    current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(opened_price) - float(current_price)
    logging.info(
        f'Entry Price: {opened_price} --- Current Price: {current_price} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list_scalping) - 1):
        if config.checkpoint_list_scalping[i] <= current_profit < config.checkpoint_list_scalping[i + 1]:
            if current_checkpoint != config.checkpoint_list_scalping[i]:
                current_checkpoint = config.checkpoint_list_scalping[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    stop_loss = float(opened_price) + config.SL
    # Checking Stop Loss Condition
    if float(current_price) <= stop_loss:
        logging.info('Break even price passed!')
        files_manager.insert_scalping_data(opened_price, current_price, current_profit)
        if iteration_count >= 7000 and len(profit_checkpoint_list) == 0:
            return 'Loss'
    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[
        -2] is not None and iteration_count >= random.randint(2000, 5000):
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if current_profit < profit_checkpoint_list[-2] or current_checkpoint >= config.checkpoint_list_scalping[-1]:
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            position_size = config.position_size
            save_data = (position_size * float(current_price)) / 100
            files_manager.insert_scalping_data(opened_price, current_price, current_profit, round(save_data, 3),
                                               iteration_count)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'
    if len(profit_checkpoint_list) > 0 and current_profit <= profit_checkpoint_list[0]:
        body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        position_size = config.position_size
        save_data = (position_size * float(current_price)) / 100
        files_manager.insert_scalping_data(opened_price, current_price, current_profit, round(save_data, 3),
                                           iteration_count)
        logging.info('Saving data')
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')

        return 'Profit'
