import time
from matic import matic_trade, trade_simulate
import threading
import logging_settings

data = None
is_empty = False


def run_trade(cryptocurrency, price, action):
    if cryptocurrency == 'MATICUSDT':
        start_time = time.time()
        print(f'Starting trade for symbol {cryptocurrency} ---> side: {action} ---> price: {price} ---> '
              f'trade start time: {start_time}')
        matic_trade.trade(cryptocurrency, action, price)
        logging_settings.actions_logger.info(f'Starting trade for symbol {cryptocurrency} '
                                             f'---> side: {action} ---> price: {price}')
    else:
        print(f"Unknown cryptocurrency: {cryptocurrency}")


