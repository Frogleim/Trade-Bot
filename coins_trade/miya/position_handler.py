from binance.client import Client
from . import config, db
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
my_db = db.DataBase()
API_KEY, API_SECRET = my_db.get_binance_keys()
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def close_position(side, quantity):
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
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
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
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
    client = Client(api_key=API_KEY, api_secret=API_SECRET)

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
