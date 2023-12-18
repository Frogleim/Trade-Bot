from binance.client import Client
import pnl_calculator, crypto_ticker, config, files_manager, moving_avarage, trade_with_me
import logging
# import config
import time
import os
import sys

api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(api_key, api_secret)
current_checkpoint = None
checking_price = None
profit_checkpoint_list = []
current_profit = 0

price_history = []
SMA = 0.0


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
            if (trade_with_me.predict_crypto()['trading_signal'] > 0
                    and trade_with_me.predict_crypto()['predicted_prob'] >= 0.9):
                logging.info(f'Crypto Direction: {pnl_calculator.get_last_two_candles_direction(config.trading_pair)}')
                logging.info(pnl_calculator.get_last_two_candles_direction(config.trading_pair))
                message = (f"{config.trading_pair} goes up for more than {config.signal_price}$\n"
                           f" Buying {config.trading_pair} for {round(float(next_crypto_current), 1)}$")
                logging.info(message)
                return True, next_crypto_current, signal_difference
            elif (trade_with_me.predict_crypto()['trading_signal'] < 0
                  and trade_with_me.predict_crypto()['predicted_prob'] >= 0.9):
                logging.info(f'Crypto Direction: {pnl_calculator.get_last_two_candles_direction(config.trading_pair)}')
                logging.info(pnl_calculator.get_last_two_candles_direction(config.trading_pair))
                message = (f"{config.trading_pair} goes down for more than {config.signal_price}$\n"
                           f" Selling {config.trading_pair} for {round(float(next_crypto_current), 1)}$")
                logging.info(message)
                return False, next_crypto_current, signal_difference
            else:
                continue


def trade():
    crypto_price_change, opened_price, signal_price = check_price_changes()
    if crypto_price_change:
        print(f'Buying {config.trading_pair}')
        while True:
            res = pnl_long(opened_price=opened_price, signal=signal_price)
            if res == 'Profit':
                # try:
                #     crypto_ticker.close_position(side='long', quantity=config.position_size)
                # except Exception as e:
                #     logging.error(e)
                #     crypto_ticker.close_position(side='long', quantity=config.position_size)
                pnl_calculator.position_size()
                logging.info('Position closed')
                break
    elif not crypto_price_change:
        print(f'Selling {config.trading_pair}')
        while True:
            res = pnl_short(opened_price=opened_price, signal=signal_price)
            if res == 'Profit':
                # try:
                #     crypto_ticker.close_position(side='long', quantity=config.position_size)
                # except Exception as e:
                #     logging.error(e)
                #     crypto_ticker.close_position(side='long', quantity=config.position_size)
                pnl_calculator.position_size()
                logging.info('Position closed')
                break


def pnl_long(opened_price=None, current_price=2090, signal=None):
    global current_profit, current_checkpoint, profit_checkpoint_list
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(btc_current) - float(opened_price)
    print(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.long_term_checkpoints) - 1):
        if config.long_term_checkpoints[i] <= current_profit < config.long_term_checkpoints[i + 1]:
            if current_checkpoint != config.long_term_checkpoints[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.long_term_checkpoints[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.long_term_checkpoints[-1]:
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
    for i in range(len(config.long_term_checkpoints) - 1):
        if config.long_term_checkpoints[i] <= current_profit < config.long_term_checkpoints[i + 1]:
            if current_checkpoint != config.long_term_checkpoints[i]:
                current_checkpoint = config.long_term_checkpoints[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.long_term_checkpoints[-1]:
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
    import build_model

    while True:
        build_model.train_base_model()
        trade()
