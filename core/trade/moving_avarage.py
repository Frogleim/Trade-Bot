import numpy as np
from binance.client import Client
import ccxt
import pandas as pd

price_history = []

api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
client = Client(api_key, api_secret)

# Function to calculate the moving average
def calculate_sma(price_history, window_size):
    if len(price_history) < window_size:
        return None
    else:
        return sum(price_history[-window_size:]) / window_size



