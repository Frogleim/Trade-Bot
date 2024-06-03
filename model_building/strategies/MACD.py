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
import joblib

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


# Backtest function with take profit and stop loss
def backtest(signals, capital, take_profit, stop_loss):
    positions = []
    balance = capital
    btc_balance = 0
    entry_price = 0
    for i in range(len(signals)):
        if signals['signals'][i] == 1 and btc_balance == 0:  # Buy signal
            btc_balance = balance / signals['Close'][i]
            balance = 0
            entry_price = signals['Close'][i]
            positions.append(('Buy', signals.index[i], signals['Close'][i], btc_balance))
        elif btc_balance > 0:
            price_change = (signals['Close'][i] - entry_price) / entry_price
            if price_change >= take_profit or price_change <= stop_loss:
                balance = btc_balance * signals['Close'][i]
                btc_balance = 0
                positions.append(('Sell', signals.index[i], signals['Close'][i], balance))
    return positions, balance


# Main execution
if __name__ == "__main__":
    starting_capital = 100  # Starting capital in USD
    take_profit = 0.060  # 0.6%
    stop_loss = -0.0045  # -0.45%

    data = fetch_binance_data(ticker, "1 Jan 2023", "1 Jan 2024", interval)
    signals = signal_generation(data, macd, ma1, ma2)
    positions, final_balance = backtest(signals, starting_capital, take_profit, stop_loss)

    # Save results to CSV
    results = pd.DataFrame(positions, columns=['Action', 'Date', 'Price', 'Balance/Qty'])
    results.to_csv('./backtesting/backtest_results.csv', index=False)
