import time

# from . import bitcoin_ticker, config
# from . import logs_handler
import bitcoin_ticker
import logs_handler
import logging
import random
import config
import os

current_profit = 0
position_mode = None
profit_checkpoint_list = []
current_checkpoint = None
THRESHOLD_FOR_CLOSING = -30
LOSS = False
checking_price = None

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "binance_bot")
logging.basicConfig(filename=f'{files_dir}/logs/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def trade():
    btc_price_change, opened_price = check_price_changes()
    if btc_price_change:
        # bitcoin_ticker.create_order(side='long')
        body = f'Buying ETHUSDT for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            res = pnl_long(opened_price=opened_price)
            if res == 'Profit':
                # bitcoin_ticker.close_position(side='short', quantity=config.position_size)
                logging.info('Position closed')
                log = logs_handler.read_logs_txt()
                trade_log = ''.join(log)
                break
            elif res == 'Loss':
                # bitcoin_ticker.close_position(side='short', quantity=config.position_size)
                logging.info('Position closed')
                log = logs_handler.read_logs_txt()
                trade_log = ''.join(log)
                break
            time.sleep(random.uniform(0.6587, 1.11))
    else:
        # bitcoin_ticker.create_order(side='short')
        body = f'Selling ETHUSDT for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            res = pnl_short(opened_price=opened_price)
            if res == 'Profit':
                # bitcoin_ticker.close_position(side='long', quantity=config.position_size)
                logging.info('Position closed')
                log = logs_handler.read_logs_txt()
                trade_log = ''.join(log)
                break
            elif res == 'Loss':
                # bitcoin_ticker.close_position(side='long', quantity=config.position_size)
                logging.info('Position closed')
                log = logs_handler.read_logs_txt()
                trade_log = ''.join(log)
                break
            time.sleep(random.uniform(0.6587, 1.11))


def check_price_changes():
    global checking_price

    while True:
        btc_current_class = bitcoin_ticker.LivePrice()
        btc_current = btc_current_class.get_live_price()
        print(btc_current)
        checking_price = btc_current
        time.sleep(config.ticker_timeout)
        next_btc_current_class = bitcoin_ticker.LivePrice()
        next_btc_current = next_btc_current_class.get_live_price()
        if float(next_btc_current) - float(checking_price) > 1.5:
            message = f"ETHUSDT goes up for more than 1$\n Buying ETHUSDT for {round(float(next_btc_current), 1)}$"
            logging.info(message)
            return True, next_btc_current
        elif float(next_btc_current) - float(checking_price) < -1.5:
            message = f"ETHUSDT goes up for more than 1$\n Buying ETHUSDT for {round(float(next_btc_current), 1)}$"
            logging.info(message)

            return False, next_btc_current
        else:
            message = f"ETHUSDT price doesnt changed enough! Current price: {round(float(next_btc_current), 1)}"
            logging.info(message)

            continue


def pnl_long(opened_price=None, current_price=2090):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current_class = bitcoin_ticker.LivePrice()
    btc_current = btc_current_class.get_live_price()
    trading_pair = 'ETHUSDT'
    current_profit = float(btc_current) - float(opened_price)
    print(current_profit)
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
        elif current_profit <= -5:  # Stop loss on -9.52%
            LOSS = True
            logging.info('Losing money')

    print('Checking checkpoints')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            print('Position closed!')
            profit_checkpoint_list = []
            print(current_profit)
            body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            return 'Profit'
    elif LOSS:
        body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        return 'Loss'


def pnl_short(opened_price=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current_class = bitcoin_ticker.LivePrice()
    btc_current = btc_current_class.get_live_price()
    trading_pair = 'ETHUSDT'
    current_profit = float(opened_price) - float(btc_current)
    print(current_profit)
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
        elif current_profit <= -5:  # Stop loss on -9.52%
            LOSS = True
            logging.warning('Losing money')

    print('Checking checkpoints')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint > profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            profit_checkpoint_list = []
            body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            return 'Profit'
    elif LOSS:
        body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        return 'Loss'


if __name__ == '__main__':
    while True:
        trade()
        time.sleep(10)
