from binance.client import Client
import config
import logging
import os

previous_price = None
alert_status = False
return_response = None
price_threshold = 15
price_difference = 0.0
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
logging.basicConfig(
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'



def get_account_balance(client):
    account_info = client.futures_account()
    balance = float(account_info['totalWalletBalance'])
    return balance


def get_ask_price(client, symbol):
    order_book = client.get_order_book(symbol=symbol)
    ask_price = float(order_book['asks'][0][0])
    return ask_price


def create_order(entry_price, side, percentage_of_balance=95, quantity=None):
    client = Client(api_key=api_key, api_secret=api_secret)
    symbol = 'ETHUSDT'
    if side == 'long':
        order = client.futures_create_order(
            symbol=config.trading_pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
        print(order)
        print("Order opened successfully")

    elif side == 'short':
        order = client.futures_create_order(
            symbol=config.trading_pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,

        )
        print(order)
        print("Order opened successfully")


def close_position(side, quantity):
    client = Client(api_key=api_key, api_secret=api_secret)
    if side == 'long':
        order = client.futures_create_order(
            symbol=config.trading_pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
    else:
        order = client.futures_create_order(
            symbol=config.trading_pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,

            quantity=quantity,
        )
    print(order)
    print("Position closed successfully")


def place_buy_order(price, quantity, symbol):
    client = Client(api_key=api_key, api_secret=api_secret)
    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type='LIMIT',
        timeInForce='GTC',  # Good 'til canceled
        quantity=quantity,
        price=price
    )

    print("Buy order placed successfully:")
    print(order)
    return order


def place_sell_order(price, quantity, symbol):
    client = Client(api_key=api_key, api_secret=api_secret)

    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type='LIMIT',
        timeInForce='GTC',  # Good 'til canceled
        quantity=quantity,
        price=price
    )

    print("Sell order placed successfully:")
    return order


if __name__ == "__main__":
    place_buy_order(price=40000, quantity=0.003, symbol='BTCUSDT')
