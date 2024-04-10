import time
from matic import matic_trade, trade_simulate
import threading
import logging_settings

data = None
is_empty = False


def run_trade(cryptocurrency, price, action):
    if cryptocurrency == 'MATICUSDT':
        start_time = time.time()
        print(f'Starting trade for symbol {cryptocurrency} ---> side: {action} ---> price: {price}')
        trade_simulate.trade(cryptocurrency, action, price, start_time)
        logging_settings.actions_logger.info(f'Starting trade for symbol {cryptocurrency} '
                                             f'---> side: {action} ---> price: {price}')
    else:
        print(f"Unknown cryptocurrency: {cryptocurrency}")


