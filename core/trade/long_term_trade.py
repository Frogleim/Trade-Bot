from binance.client import Client
import pnl_calculator, crypto_ticker, config, files_manager
import logging
import time
import os

api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(api_key, api_secret)
current_checkpoint = None
checking_price = None
profit_checkpoint_list = []
current_profit = 0
price_history = []
SMA = 0.0
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "trade")


def check_price_changes():
    global checking_price, price_history, SMA
    price_history = []  # Keep track of historical prices
    while True:
        crypto_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'Current {config.trading_pair} price: {crypto_current}')
        checking_price = crypto_current
        time.sleep(config.ticker_timeout)
        next_crypto_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'New {config.trading_pair} price: {next_crypto_current} SMA: {SMA}')
        signal_difference = float(next_crypto_current) - float(checking_price)
        logging.info(f'Difference: {round(signal_difference, 2)}')
        return True, next_crypto_current, signal_difference


def trade():
    global current_checkpoint
    pnl_calculator.check_wallet()
    df, model = build_model.train_model()
    window_size = 3  # You can adjust the window size as needed
    df['SMA'] = df['trading_signal'].rolling(window=window_size).mean()
    df['Trend'] = 'None'
    df.loc[df['SMA'] > 0, 'Trend'] = 'Up'
    df.loc[df['SMA'] < 0, 'Trend'] = 'Down'
    data = df[['date', 'trading_signal', 'SMA', 'Trend']].iloc[-1]

    btc_price_change, opened_price, signal_price = check_price_changes()
    if data['Trend'] == 'Up':
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
            if open_orders['status'] == 'NEW':
                if float(ticker) - float(open_orders['price']) > 3:
                    client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
                    break
            if open_orders['status'] == 'FILLED':
                res = check_profit_long(opened_price)
                if res == 'Profit':
                    try:
                        crypto_ticker.close_position(side='short', quantity=config.position_size)
                    except Exception as e:
                        logging.error(e)
                        crypto_ticker.close_position(side='short', quantity=config.position_size)
                    pnl_calculator.position_size()
                    logging.info('Position closed')
                    break
    elif data['Trend'] == 'Down':
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
            if open_orders['status'] == 'NEW':
                if float(open_orders['price']) - float(ticker) < -3:
                    client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
                    break

            if open_orders['status'] == 'FILLED':
                res = check_profit_short(opened_price)
                if res == 'Profit':
                    try:
                        crypto_ticker.close_position(side='long', quantity=config.position_size)
                    except Exception as e:
                        logging.error(e)
                        crypto_ticker.close_position(side='long', quantity=config.position_size)
                    pnl_calculator.position_size()
                    logging.info('Position closed')
                    break


def check_profit_long(opened_price):
    global current_profit, current_checkpoint, profit_checkpoint_list
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(btc_current) - float(opened_price)
    if current_profit >= 8:
        files_manager.insert_data(opened_price, btc_current, current_profit)
        return 'Profit'


def check_profit_short(opened_price):
    global current_profit, current_checkpoint, profit_checkpoint_list
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(opened_price) - float(btc_current)
    if current_profit >= 8:
        files_manager.insert_data(opened_price, btc_current, current_profit)
        return 'Profit'


if __name__ == '__main__':
    import build_model
    #
    count = 0
    while True:
        trade()
        count += 1
        if count == 4:
            count = 0
            time.sleep(2 * 3600)
