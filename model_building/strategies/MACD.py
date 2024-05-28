# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 11:57:46 2018

@author: Administrator
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from binance.client import Client
from binance.enums import HistoricalKlinesType
from binance import ThreadedWebsocketManager
import os

# Initialize Binance client
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
client = Client(api_key, api_secret)

# Global variables to hold the moving averages and other parameters
ma1 = 12
ma2 = 26
ticker = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE


# Simple moving average
def macd(signals, ma1, ma2):
    signals['ma1'] = signals['Close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['Close'].rolling(window=ma2, min_periods=1, center=False).mean()
    return signals


# Signal generation
def signal_generation(df, method, ma1, ma2):
    signals = method(df, ma1, ma2)
    signals['positions'] = 0
    signals['positions'][ma1:] = np.where(signals['ma1'][ma1:] >= signals['ma2'][ma1:], 1, 0)
    signals['signals'] = signals['positions'].diff()
    signals['oscillator'] = signals['ma1'] - signals['ma2']
    return signals


# Fetch historical data from Binance
def fetch_binance_data(ticker, start_date, end_date, interval):
    klines = client.get_historical_klines(ticker, interval, start_date, end_date,
                                          klines_type=HistoricalKlinesType.FUTURES)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time',
        'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume',
        'Taker_buy_quote_asset_volume', 'Ignore'
    ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return data


# Update DataFrame with new price data
def update_data(df, new_data):
    new_df = pd.DataFrame([new_data], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
    new_df.set_index('timestamp', inplace=True)
    new_df = new_df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    df = pd.concat([df, new_df])
    return df


# Write signals to a text file
def write_signal_to_file(signal_data):
    with open('./backtesting/backtesting_15min.txt', 'a') as f:
        f.write(f"{signal_data}\n")


# Process message from WebSocket
def process_message(msg):
    global df, ma1, ma2
    new_data = [msg['E'], msg['k']['o'], msg['k']['h'], msg['k']['l'], msg['k']['c'], msg['k']['v']]
    df = update_data(df, new_data)
    df = signal_generation(df, macd, ma1, ma2)
    latest_signal = df.iloc[-1]
    signal_data = {
        'timestamp': latest_signal.name,
        'Close': latest_signal['Close'],
        'ma1': latest_signal['ma1'],
        'ma2': latest_signal['ma2'],
        'positions': latest_signal['positions'],
        'signals': latest_signal['signals'],
        'oscillator': latest_signal['oscillator']
    }
    write_signal_to_file(signal_data)
    print(latest_signal)  # Print the latest signal


# Main function to start WebSocket and fetch initial data
def main():
    global df, ma1, ma2, ticker, interval
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    # Fetch historical data
    df = fetch_binance_data(ticker, start_date, end_date, interval)
    df = signal_generation(df, macd, ma1, ma2)

    # Start WebSocket manager
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    # Subscribe to the kline WebSocket
    twm.start_kline_socket(callback=process_message, symbol=ticker, interval=interval)

    # Keep the script running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        twm.stop()


if __name__ == '__main__':
    main()
