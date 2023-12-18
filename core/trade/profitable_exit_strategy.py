from binance.client import Client
from . import pnl_calculator, crypto_ticker, config, files_manager, moving_avarage, trade_with_me
import logging
# import config
import time
import os
import sys

current_profit = 0
profit_checkpoint_list = []
SMA = 0.0
current_checkpoint = None
checking_price = None
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'

api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(api_key, api_secret)
price_history = []

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "Trade-Bot")
logging.basicConfig(filename=f'{files_dir}/logs/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
error_handler = logging.FileHandler(f'{files_dir}/logs/error_logs.log')
error_handler.setLevel(logging.ERROR)  # Set the desired log level for the file
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
error_console_handler = logging.StreamHandler(sys.stdout)
error_console_handler.setLevel(logging.ERROR)  # Set the desired log level for the console
error_console_handler.setFormatter(error_formatter)
error_logger.addHandler(error_console_handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


def trade():
    btc_price_change, opened_price, signal_price = check_price_changes()
    global current_checkpoint
    if btc_price_change:
        profit_checkpoint_list.clear()
        current_checkpoint = None
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list} --- Current checkpoint: {current_checkpoint}')
        try:
            order_info = crypto_ticker.place_buy_order(price=opened_price, quantity=config.position_size,
                                                       symbol=config.trading_pair)
        except Exception as e:
            logging.error(e)
            order_info = crypto_ticker.place_buy_order(price=opened_price, quantity=config.position_size,
                                                       symbol=config.trading_pair)
        body = f'Buying {config.trading_pair} for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            open_orders = client.futures_get_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
            if float(ticker) - float(open_orders['price']) > 3:
                client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
                break
            if open_orders['status'] == 'FILLED':
                res = pnl_long(opened_price=open_orders['price'], signal=signal_price)
                if res == 'Profit':
                    try:
                        crypto_ticker.close_position(side='short', quantity=config.position_size)
                    except Exception as e:
                        logging.error(e)
                        crypto_ticker.close_position(side='short', quantity=config.position_size)
                    pnl_calculator.position_size()
                    logging.info('Position closed')
                    break
            else:
                continue
    elif not btc_price_change:
        profit_checkpoint_list.clear()
        current_checkpoint = None
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list} --- Current checkpoint: {current_checkpoint}')
        try:
            order_info = crypto_ticker.place_sell_order(price=opened_price, quantity=config.position_size,
                                                        symbol=config.trading_pair)
        except Exception as e:
            logging.error(e)
            order_info = crypto_ticker.place_sell_order(price=opened_price, quantity=config.position_size,
                                                        symbol=config.trading_pair)
        body = f'Selling {config.trading_pair} for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            open_orders = client.futures_get_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
            if float(open_orders['price']) - float(ticker) < -3:
                client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
                break

            if open_orders['status'] == 'FILLED':
                res = pnl_short(opened_price=open_orders['price'], signal=signal_price)
                if res == 'Profit':
                    try:
                        crypto_ticker.close_position(side='long', quantity=config.position_size)
                    except Exception as e:
                        logging.error(e)
                        crypto_ticker.close_position(side='long', quantity=config.position_size)
                    pnl_calculator.position_size()
                    logging.info('Position closed')
                    break
            else:
                continue


def check_price_changes():
    global checking_price, price_history, SMA
    window_size = 10  # Adjust the window size as needed
    price_history = []  # Keep track of historical prices
    while True:
        crypto_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'Current {config.trading_pair} price: {crypto_current}')
        checking_price = crypto_current
        price_history.append(float(crypto_current))
        if len(price_history) > window_size:
            price_history = price_history[-window_size:]
        SMA = moving_avarage.calculate_sma(price_history, window_size)
        logging.info(f'SMA: {SMA}')
        time.sleep(config.ticker_timeout)
        next_crypto_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'New {config.trading_pair} price: {next_crypto_current} SMA: {SMA}')
        signal_difference = float(next_crypto_current) - float(checking_price)
        logging.info(f'Difference: {round(signal_difference, 2)}')
        if SMA is not None:
            if (float(crypto_current) > SMA and trade_with_me.predict_crypto()['trading_signal'] > 0
                    and trade_with_me.predict_crypto()['predicted_prob'] >= 0.9):
                logging.info(f'Crypto Direction: {pnl_calculator.get_last_two_candles_direction(config.trading_pair)}')
                logging.info(pnl_calculator.get_last_two_candles_direction(config.trading_pair))
                message = (f"{config.trading_pair} goes up for more than {config.signal_price}$\n"
                           f" Buying {config.trading_pair} for {round(float(next_crypto_current), 1)}$")
                logging.info(message)
                return True, next_crypto_current, signal_difference
            elif (float(
                    crypto_current) < SMA and trade_with_me.predict_crypto()['trading_signal'] < 0
                  and trade_with_me.predict_crypto()['predicted_prob'] >= 0.9):
                logging.info(f'Crypto Direction: {pnl_calculator.get_last_two_candles_direction(config.trading_pair)}')
                logging.info(pnl_calculator.get_last_two_candles_direction(config.trading_pair))
                message = (f"{config.trading_pair} goes down for more than {config.signal_price}$\n"
                           f" Selling {config.trading_pair} for {round(float(next_crypto_current), 1)}$")
                logging.info(message)
                return False, next_crypto_current, signal_difference
            else:
                continue
        time.sleep(40)


def pnl_long(opened_price=None, current_price=2090, signal=None):
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

    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            body = \
                f'Position closed!.\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            position_size = config.position_size
            save_data = (position_size * float(btc_current)) / 100
            files_manager.insert_data(opened_price, btc_current, current_profit, signal, round(save_data, 3))
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


def pnl_short(opened_price=None, signal=None):
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

    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            position_size = config.position_size
            save_data = (position_size * float(btc_current)) / 100
            files_manager.insert_data(opened_price, btc_current, current_profit, signal, round(save_data, 3))
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


if __name__ == '__main__':
    while True:
        trade()
