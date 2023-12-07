import time
import config
# from . import config
import os
from binance.client import Client
import requests
from binance.helpers import round_step_size  # add at top
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "core")
print(files_dir)
client = Client(api_key='iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh',
                api_secret='hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI')

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
    original_value = config.position_size
    percentage_increase = 0.50
    new_value = original_value + (original_value * percentage_increase)
    print("Original Value:", original_value)
    print("Percentage Increase:", percentage_increase)
    print("New Value:", new_value)
    time.sleep(1)
    config.position_size = new_value
    with open(f'{files_dir}/config.py', 'r') as config_file:
        config_data = config_file.read()
    config_data = config_data.replace(f"position_size = {original_value}", f"position_size = {round(new_value, 3)}")
    with open(f'{files_dir}/config.py', 'w') as config_file:
        config_file.write(config_data)
    return original_value




def get_last_two_candles_direction(symbol, interval='5m'):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=5)
    close_prices = [float(kline[4]) for kline in klines[:-1]]

    if close_prices[-1] > close_prices[-2]:
        direction = "Up"
    elif close_prices[-1] < close_prices[-2]:
        direction = "Down"
    else:
        direction = 'No Change'

    return direction


def get_futures_balance(api_key, api_secret):
    client = Client(api_key, api_secret)

    # Fetch futures account information
    futures_account_info = client.futures_account_v2()

    # Extract the total balance
    total_balance = float(futures_account_info['totalWalletBalance'])

    return total_balance

def main():
    # Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your Binance API key and secret
    api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
    api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'

    futures_balance = get_futures_balance(api_key, api_secret)

    print(f"Futures Balance: {futures_balance} USDT")


if __name__ == '__main__':
    starting_number = 11  # 0.21$
    common_ratio = 1.05  # 20% increase
    num_terms = 40
    result = geometric_progression(starting_number, common_ratio, num_terms)
    print(result)
    # Replace YOUR_API_KEY(api_key, api_secret)
    res = get_last_two_candles_direction(symbol=config.trading_pair)
    print(res)