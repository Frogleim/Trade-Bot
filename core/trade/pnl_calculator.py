import logging
# from . import config
import os
import moving_avarage
import config
from binance.client import Client
import math

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)

files_dir = os.path.join(parent_dir, "trade")
print(files_dir)
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'

api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(config.API_KEY, config.API_SECRET)


class BinanceFuturesPNLCalculator:
    def __init__(self, entry_price, exit_price, quantity, leverage):
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.quantity = quantity
        self.leverage = leverage

    def calculate_pnl(self):
        pnl = ((self.exit_price - self.entry_price) / self.entry_price) * self.quantity * self.leverage
        return pnl


def geometric_progression(starting_number, ratio, count):
    """
    Generate a geometric progression.

    Parameters:
    - starting_number: The first term of the geometric progression.
    - ratio: The common ratio.
    - count: The number of terms to generate.

    Returns:
    A list containing the terms of the geometric progression.
    """
    progression = [starting_number * (ratio ** i) for i in range(count)]
    return progression


def calculate_modified_difference(lst):
    modified_values = [(lst[i] - lst[i + 1]) * (1 - 0.005) for i in range(len(lst) - 1)]
    return modified_values


def position_size():
    file_original_value = config.position_size
    crypto_current_price = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    percentage_increase = 0.05
    new_value = file_original_value + (file_original_value * percentage_increase)
    original_value = (float(file_original_value) * float(crypto_current_price)) / 100
    logging_new_value = (new_value * float(crypto_current_price)) / 100
    logging.info(f"Original Value: {round(original_value, 3)}", )
    logging.info(f"Percentage Increase: {round(percentage_increase * 100)}%", )
    logging.info(f"New Value: {round(logging_new_value, 3)}$", )
    final_position = math.ceil(new_value * 100) / 100
    config.position_size = round(new_value, 3)
    with open(f'{files_dir}/config.py', 'r') as config_file:
        config_data = config_file.read()
    config_data = config_data.replace(f"position_size = {file_original_value}",
                                      f"position_size = {round(new_value, 2)}")
    with open(f'{files_dir}/config.py', 'w') as config_file:
        config_file.write(config_data)
    return final_position


def get_symbol_precision(symbol):
    exchange_info = client.get_exchange_info()

    for symbol_info in exchange_info['symbols']:
        if symbol_info['symbol'] == symbol:
            return int(symbol_info['baseAssetPrecision'])

    # If the symbol is not found, you may want to handle this case appropriately
    raise ValueError(f"Symbol {symbol} not found in exchange info")


def are_last_3_candles_growing(api_key, api_secret, symbol="ETHUSDT", interval="5m"):
    client = Client(api_key, api_secret)
    orders = client.get_all_orders(symbol=symbol)
    print(orders)


def get_last_two_candles_direction(symbol, interval='1m'):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=10)
    close_prices = [float(kline[4]) for kline in klines[:-1]]
    print(close_prices)
    sma = moving_avarage.calculate_sma(close_prices, config.moving_average_window)
    print(sma)

    if close_prices[-1] > close_prices[-2]:
        direction = "Up"
    elif close_prices[-1] < close_prices[-2]:
        direction = "Down"
    else:
        direction = 'No Change'

    return direction


def get_current_positions():
    binance_balance = []
    # Replace YOUR_API_KEY and YOUR_API_SECRET with your Binance API key and secret
    client = Client(api_key, api_secret)
    futures_account_info = client.futures_account()
    for asset in futures_account_info['assets']:
        asset_name = asset['asset']
        wallet_balance = asset['walletBalance']
        balance = {
            'asset':
                f'{asset_name} - Wallet Balance: {wallet_balance}'
        }
        print(f'{asset_name} - Wallet Balance: {wallet_balance}')
        binance_balance.append(balance)


if __name__ == '__main__':
    starting_number = 1.449  # 0.21$
    common_ratio = 1.05  # 20% increase
    num_terms = 100  # 40 Trades is one day trade
    result = geometric_progression(starting_number, common_ratio, num_terms)
    print(result)
    wallet = [new_value + 9.3 for new_value in result]
    print(wallet)
    res = get_last_two_candles_direction(symbol=config.trading_pair)
    print(res)
    are_last_3_candles_growing(api_key, api_secret, config.trading_pair)
