import time

import pandas as pd
from binance.client import Client
import tp_sl, config, pnl_calculator, position_handler
import os
import json
import logging
import sys

# Replace with your Binance API key and secret
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(api_key, api_secret)
interval = '5m'
length = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
closed = False


def calculate_bollinger_bands(interval, length, num_std_dev):
    try:
        klines = client.futures_klines(symbol='XRPUSDT', interval=interval)
    except Exception:
        klines = client.futures_klines(symbol='XRPUSDT', interval=interval)

    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = df['close'].rolling(window=length).mean()
    df['std_dev'] = df['close'].rolling(window=length).std()
    df['upper_band'] = df['sma'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['sma'] - (num_std_dev * df['std_dev'])
    return df


def is_sideways_market(data, num_periods):
    bollinger_values = data.iloc[-num_periods:][['upper_band', 'lower_band', 'close']]
    upper_band, lower_band = bollinger_values['upper_band'].iloc[-1], bollinger_values['lower_band'].iloc[-1]
    close_price = bollinger_values['close'].iloc[-2]
    print(f'Lower Band: {lower_band} --> Upper Band: {upper_band} --> Close Price: {close_price}')
    if close_price < lower_band:
        return 'Long', close_price
    elif close_price > upper_band:
        return 'Short', close_price
    else:
        return 'Hold', close_price



def trade():
    global closed
    num_periods = 10
    data = calculate_bollinger_bands(interval, length, config.num_std_dev)
    signal, entry_price = is_sideways_market(data, num_periods)
    live_price = float(client.futures_ticker(symbol=config.trading_pair)['lastPrice'])

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
            ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            open_orders = client.futures_get_order(symbol=config.trading_pair,
                                                   orderId=int(order_info['orderId']))
            if open_orders['status'] == 'NEW':
                if float(ticker) - float(open_orders['price']) < -0.06 or float(ticker) - float(open_orders['price']) > 0.06:
                    client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
                    break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_short(entry_price)
                if res == 'Profit':
                    print(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=config.position_size)
                    except Exception as e:
                        print(e)
                        position_handler.close_position(side='long', quantity=config.position_size)
                    pnl_calculator.position_size()
                    break
    if signal == 'Long':
        tp_sl.profit_checkpoint_list.clear()
        try:
            order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
                                                          symbol=config.trading_pair)
        except Exception as e:
            print(e)
            order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
                                                          symbol=config.trading_pair)
        while True:
            ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            open_orders = client.futures_get_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
            if open_orders['status'] == 'NEW':
                if float(ticker) - float(open_orders['price']) > 0.06 or float(ticker) - float(open_orders['price']) < -0.06:
                    client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
                    break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_long(entry_price)
                if res == 'Profit':
                    print(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=config.position_size)
                    except Exception as e:
                        print(e)
                        position_handler.close_position(side='short', quantity=config.position_size)
                    pnl_calculator.position_size()
                    break


if __name__ == '__main__':

    while True:
        tp_sl.current_checkpoint = None
        trade()
