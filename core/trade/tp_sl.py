# from . import config, files_manager
import logging
from binance.client import Client
from collections import Counter
from . import config, files_manager
# import config, files_manager
# import files_manager
import sys

client = Client()
current_profit = 0
profit_checkpoint_list = []
SMA = 0.0
current_checkpoint = None
checking_price = None
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'

api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
price_history = []

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)


def pnl_long(opened_price, sma):
    global current_profit, current_checkpoint, profit_checkpoint_list
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(btc_current) - float(opened_price)
    print(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if float(btc_current) <= float(sma):
        files_manager.insert_data(opened_price, btc_current, current_profit)

        return 'Loss'
    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        print('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        print(f'Checkpoint List is: {profit_checkpoint_list}')
        if current_checkpoint < profit_checkpoint_list[-1] - 2 or current_checkpoint >= config.checkpoint_list[-1]:
            body = \
                f'Position closed!.\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            position_size = config.position_size
            save_data = (position_size * float(btc_current)) / 100
            files_manager.insert_data(opened_price, btc_current, current_profit, round(save_data, 3))
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


def pnl_short(opened_price, sma):
    global current_profit, current_checkpoint, profit_checkpoint_list
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(opened_price) - float(btc_current)
    print(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if float(btc_current) >= float(sma):
        files_manager.insert_data(opened_price, btc_current, current_profit)
        return 'Loss'
    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        print('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        print(f'Checkpoint List is: {profit_checkpoint_list}')
        if current_checkpoint < profit_checkpoint_list[-1] - 2 or current_checkpoint >= config.checkpoint_list[-1]:
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            position_size = config.position_size
            save_data = (position_size * float(btc_current)) / 100
            files_manager.insert_data(opened_price, btc_current, current_profit, round(save_data, 3))
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'



if __name__ == '__main__':
    profit_checkpoint_list.clear()
    print(profit_checkpoint_list)
    while True:
        res = pnl_long(opened_price=2290, sma=2301)
        print(res)
        if res == 'Profit':
            print('Closing with profit')
            break
        if res == 'Loss':
            print('Closing with Loss')
            break