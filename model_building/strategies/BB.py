# coding: utf-8

"""
Created on Tue Feb  6 11:57:46 2018

@author: Administrator
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import copy
import numpy as np
from binance.client import Client
from binance.enums import HistoricalKlinesType

# Initialize Binance client
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
client = Client(api_key, api_secret)


# Calculate moving average and moving standard deviation
def bollinger_bands(df):
    data = copy.deepcopy(df)
    data['std'] = data['Close'].rolling(window=20, min_periods=20).std()
    data['mid band'] = data['Close'].rolling(window=20, min_periods=20).mean()
    data['upper band'] = data['mid band'] + 2 * data['std']
    data['lower band'] = data['mid band'] - 2 * data['std']
    return data


# Signal generation
def signal_generation(data, method):
    period = 75
    alpha = 0.0001
    beta = 0.0001

    df = method(data)
    df['signals'] = 0
    df['cumsum'] = 0
    df['coordinates'] = ''

    for i in range(period, len(df)):
        moveon = False
        threshold = 0.0

        if (df['Close'][i] > df['upper band'][i]) and (df['cumsum'][i] == 0):
            for j in range(i, i - period, -1):
                if (np.abs(df['mid band'][j] - df['Close'][j]) < alpha) and (
                        np.abs(df['mid band'][j] - df['upper band'][i]) < alpha):
                    moveon = True
                    break
            if moveon:
                moveon = False
                for k in range(j, i - period, -1):
                    if (np.abs(df['lower band'][k] - df['Close'][k]) < alpha):
                        threshold = df['Close'][k]
                        moveon = True
                        break
            if moveon:
                moveon = False
                for l in range(k, i - period, -1):
                    if (df['mid band'][l] < df['Close'][l]):
                        moveon = True
                        break
            if moveon:
                moveon = False
                for m in range(i, j, -1):
                    if (df['Close'][m] - df['lower band'][m] < alpha) and (df['Close'][m] > df['lower band'][m]) and (
                            df['Close'][m] < threshold):
                        df.at[i, 'signals'] = 1
                        df.at[i, 'coordinates'] = '%s,%s,%s,%s,%s' % (l, k, j, m, i)
                        df['cumsum'] = df['signals'].cumsum()
                        moveon = True
                        break
        if (df['cumsum'][i] != 0) and (df['std'][i] < beta) and (not moveon):
            df.at[i, 'signals'] = -1
            df['cumsum'] = df['signals'].cumsum()
    return df


# Visualization
def plot(new):
    if new[new['signals'] != 0].empty:
        print("No signals generated, cannot plot.")
        return

    a, b = list(new[new['signals'] != 0].iloc[:2].index)
    newbie = new[a - 85:b + 30]
    newbie.set_index(pd.to_datetime(newbie.index, unit='ms'), inplace=True)

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.plot(newbie['Close'], label='price')
    ax.fill_between(newbie.index, newbie['lower band'], newbie['upper band'], alpha=0.2, color='#45ADA8')
    ax.plot(newbie['mid band'], linestyle='--', label='moving average', c='#132226')
    ax.plot(newbie['Close'][newbie['signals'] == 1], marker='^', markersize=12, lw=0, c='g', label='LONG')
    ax.plot(newbie['Close'][newbie['signals'] == -1], marker='v', markersize=12, lw=0, c='r', label='SHORT')

    temp = newbie['coordinates'][newbie['signals'] == 1]
    indexlist = list(map(int, temp[temp.index[0]].split(',')))
    ax.plot(newbie['Close'][pd.to_datetime(new['date'].iloc[indexlist], unit='ms')], lw=5, alpha=0.7, c='#FE4365',
            label='double bottom pattern')

    plt.text((newbie.loc[newbie['signals'] == 1].index[0]), newbie['lower band'][newbie['signals'] == 1], 'Expansion',
             fontsize=15, color='#563838')
    plt.text((newbie.loc[newbie['signals'] == -1].index[0]), newbie['lower band'][newbie['signals'] == -1],
             'Contraction', fontsize=15, color='#563838')

    plt.legend(loc='best')
    plt.title('Bollinger Bands Pattern Recognition')
    plt.ylabel('price')
    plt.grid(True)
    plt.show()


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


def main():
    start_date = input('start date in format yyyy-mm-dd:')
    end_date = input('end date in format yyyy-mm-dd:')
    ticker = input('ticker (e.g., BTCUSDT):')

    df = fetch_binance_data(ticker, start_date, end_date, Client.KLINE_INTERVAL_1DAY)
    signals = signal_generation(df, bollinger_bands)
    new = copy.deepcopy(signals)
    plot(new)


if __name__ == '__main__':
    main()
