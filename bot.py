from coins_trade.miya import miya_trade, trade_simulate
from model_building.strategies import MACD
from colorama import init, Fore, Back, Style
from binance.client import Client
import pandas as pd
import numpy as np
from db import DataBase
from tqdm import tqdm
import time

init()

client = Client()
start_date = '1 Jan, 2023'
end_date = '1 May, 2024'
symbol = 'MATICUSDT'


def fetch_ohlcv(symbol='MATICUSDT', timeframe=Client.KLINE_INTERVAL_15MINUTE, limit=100):
    klines = client.futures_historical_klines(symbol=symbol, interval=timeframe, start_str=start_date, end_str=end_date)
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
               'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(klines, columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]


def generate_signals(df):
    ma1 = 12
    ma2 = 26
    signals = df.copy()
    signals['ma1'] = signals['close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['close'].rolling(window=ma2, min_periods=1, center=False).mean()
    signals['positions'] = 0
    signals['positions'][ma1:] = np.where(signals['ma1'][ma1:] >= signals['ma2'][ma1:], 1, 0)
    signals['signals'] = signals['positions'].diff()
    signals['oscillator'] = signals['ma1'] - signals['ma2']
    return signals


def start_trade():
    print(Fore.GREEN + f'Starting trade for symbol {symbol}')
    my_db = DataBase()
    signal_data = my_db.get_signal(symbol=symbol)
    if signal_data is not None:
        signal = signal_data[1]
        entry_price = signal_data[2]
        trade_simulate.trade(symbol=symbol, signal=signal, entry_price=entry_price)
    print(Fore.RED + "No trade signals at this moment")


if __name__ == '__main__':
    print(Fore.YELLOW + 'Starting trade bot...')
    while True:

        start_trade()
        time.sleep(60*3600)
