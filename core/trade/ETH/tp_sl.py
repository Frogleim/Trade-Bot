import logging
import os
import random
import sys
from collections import Counter
from binance.client import Client
import config

current_profit = 0
profit_checkpoint_list = []
current_checkpoint = None
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
try:
    client = Client(api_key, api_secret)
except Exception as e:
    print(e)
    client = Client(api_key, api_secret)
price_history = []
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "ETH")
print(files_dir)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)



def pnl_long(opened_price, iteration_count=None):
    ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    if float(ticker) - opened_price >= 8:
        return 'Profit'



def pnl_short(opened_price, iteration_count=None):
    ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    if opened_price - float(ticker) <= -8:
        return 'Profit'