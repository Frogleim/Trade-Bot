import time

import pandas as pd
import numpy as np
from binance.client import Client

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 15
long_period = 50
symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 month ago UTC'


def get_historical_data(symbol, interval, start_str):
    klines = client.futures_historical_klines(symbol, interval, start_str)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                         'taker_buy_quote_asset_volume', 'ignore'])
    data['close'] = data['close'].astype(float)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data[['close']]


def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()


def check_signal():
    data = get_historical_data(symbol, interval, start_str)
    data['EMA_short'] = calculate_ema(data['close'], short_period)
    data['EMA_long'] = calculate_ema(data['close'], long_period)

    data['Signal'] = 0
    data['Signal'] = np.where(data['EMA_short'] > data['EMA_long'], 1, -1)
    data['Crossover'] = data['Signal'].diff()

    crossover = data['Crossover'].iloc[-1]
    signal = data['Signal'].iloc[-1]
    current_short_ema = data['EMA_short'].iloc[-1]
    current_long_ema = data['EMA_long'].iloc[-1]
    last_close_price = data['close'].iloc[-1]
    crossover_point = data['close'].iloc[-2] if crossover != 0 else np.nan

    print(f"Current short EMA: {round(current_short_ema, 5)}")
    print(f"Current long EMA: {round(current_long_ema, 5)}")
    print(f"Signal: {signal}")
    print(f"Is EMA Cross: {crossover}")
    print(f"Last close price: {last_close_price}")
    if crossover != 0:
        print(f"Crossover point price: {crossover_point}")
        if float(last_close_price) > crossover_point:
            return 'Buy', last_close_price
        elif float(last_close_price) < crossover_point:
            return 'Sell', last_close_price
        else:
            return 'Hold', 0.0


if __name__ == '__main__':
    while True:
        check_signal()
        time.sleep(5)