import time
from binance.client import Client
from . import tp_sl, config, position_handler
import logging
import sys

api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(api_key, api_secret)
timestamp = client.get_server_time()['serverTime']
recv_window = 5000
interval = '3m'
length = 20
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
closed = False


async def trade(signal, entry_price):
    global closed
    start_time = time.time()
    if signal == 'Short':
        tp_sl.profit_checkpoint_list.clear()
        try:
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=config.position_size,
                                                           symbol=config.trading_pair)
        except Exception as e:
            print(e)
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=config.position_size,
                                                           symbol=config.trading_pair)
        while True:
            open_orders = client.futures_get_order(symbol=config.trading_pair,
                                                   orderId=int(order_info['orderId']),
                                                   timestamp=timestamp, recvWindow=recv_window)
            if open_orders['status'] == 'CANCELED':
                return 'Canceled'
            elif open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_short(entry_price)
                if res == 'Profit':
                    print(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=config.position_size)
                    except Exception as e:
                        print(e)
                        position_handler.close_position(side='long', quantity=config.position_size)
                    return 'Completed'
            if time.time() - start_time > 3 * 60 * 60:
                print("Trade duration exceeded 3 hours without profit. Terminating trade.")
                return 'Timeout'
    elif signal == 'Long':
        tp_sl.profit_checkpoint_list.clear()
        try:
            order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
                                                          symbol=config.trading_pair)
        except Exception as e:
            print(e)
            order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
                                                          symbol=config.trading_pair)
        while True:
            open_orders = client.futures_get_order(symbol=config.trading_pair,
                                                   orderId=int(order_info['orderId']),
                                                   timestamp=timestamp, recvWindow=recv_window)
            if open_orders['status'] == 'CANCELED':
                return 'Canceled'
            elif open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_long(entry_price)
                if res == 'Profit':
                    print(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=config.position_size)
                    except Exception as e:
                        print(e)
                        position_handler.close_position(side='short', quantity=config.position_size)
                    return 'Completed'
            if time.time() - start_time > 3 * 60 * 60:
                print("Trade duration exceeded 3 hours without profit. Terminating trade.")
                return 'Timeout'
