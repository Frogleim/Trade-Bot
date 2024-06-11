import pandas as pd
import matplotlib.pyplot as plt
import copy
import numpy as np
from binance.client import Client

# Set your API key and secret
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'

client = Client(API_KEY, API_SECRET)

# Function to calculate Bollinger Bands
def bollinger_bands(df):
    data = copy.deepcopy(df)
    data['std'] = data['Close'].rolling(window=20, min_periods=20).std()
    data['mid band'] = data['Close'].rolling(window=20, min_periods=20).mean()
    data['upper band'] = data['mid band'] + 2 * data['std']
    data['lower band'] = data['mid band'] - 2 * data['std']
    return data

# Signal generation function
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
                if (np.abs(df['mid band'][j] - df['Close'][j]) < alpha) and (np.abs(df['mid band'][j] - df['upper band'][i]) < alpha):
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
                    if (df['Close'][m] - df['lower band'][m] < alpha) and (df['Close'][m] > df['lower band'][m]) and (df['Close'][m] < threshold):
                        df.at[i, 'signals'] = 1
                        df.at[i, 'coordinates'] = '%s,%s,%s,%s,%s' % (l, k, j, m, i)
                        df['cumsum'] = df['signals'].cumsum()
                        moveon = True
                        break

        if (df['cumsum'][i] != 0) and (df['std'][i] < beta) and not moveon:
            df.at[i, 'signals'] = -1
            df['cumsum'] = df['signals'].cumsum()

    return df

# Visualization function
def plot(new):
    # Ensure there are at least two signals for plotting
    signal_indices = list(new[new['signals'] != 0].index)
    if len(signal_indices) < 2:
        print("Not enough signals to plot.")
        return

    a, b = signal_indices[:2]
    newbie = new[a - 85:b + 30]

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    ax.plot(newbie['Close'], label='price')
    ax.fill_between(newbie.index, newbie['lower band'], newbie['upper band'], alpha=0.2, color='#45ADA8')
    ax.plot(newbie['mid band'], linestyle='--', label='moving average', c='#132226')
    ax.plot(newbie['Close'][newbie['signals'] == 1], marker='^', markersize=12, lw=0, c='g', label='LONG')
    ax.plot(newbie['Close'][newbie['signals'] == -1], marker='v', markersize=12, lw=0, c='r', label='SHORT')

    temp = newbie['coordinates'][newbie['signals'] == 1]
    if not temp.empty:
        indexlist = list(map(int, temp.iloc[0].split(',')))
        ax.plot(newbie['Close'].iloc[indexlist], lw=5, alpha=0.7, c='#FE4365', label='double bottom pattern')

    plt.text(newbie.loc[newbie['signals'] == 1].index[0], newbie['lower band'][newbie['signals'] == 1], 'Expansion', fontsize=15, color='#563838')
    plt.text(newbie.loc[newbie['signals'] == -1].index[0], newbie['lower band'][newbie['signals'] == -1], 'Contraction', fontsize=15, color='#563838')

    plt.legend(loc='best')
    plt.title('Bollinger Bands Pattern Recognition')
    plt.ylabel('price')
    plt.grid(True)
    plt.show()

# Backtest function
def backtest_strategy(df):
    initial_balance = 1000  # Initial balance in USDT
    balance = initial_balance
    position = 0  # Positive for long, negative for short
    position_size = 0.01  # Size of each position (0.01 units of the asset)
    entry_price = 0

    for i in range(len(df)):
        if df['signals'].iloc[i] == 1 and position <= 0:  # Buy signal
            entry_price = df['Close'].iloc[i]
            position = position_size
            print(f"Entering long position at {entry_price} on {df.index[i]}")
        elif df['signals'].iloc[i] == -1 and position >= 0:  # Sell signal
            entry_price = df['Close'].iloc[i]
            position = -position_size
            print(f"Entering short position at {entry_price} on {df.index[i]}")
        elif position > 0:  # Currently long
            balance += position * (df['Close'].iloc[i] - entry_price)
            entry_price = df['Close'].iloc[i]
        elif position < 0:  # Currently short
            balance += -position * (entry_price - df['Close'].iloc[i])
            entry_price = df['Close'].iloc[i]

    final_balance = balance
    print(f"Initial Balance: {initial_balance} USDT")
    print(f"Final Balance: {final_balance} USDT")
    print(f"Total Return: {((final_balance - initial_balance) / initial_balance) * 100:.2f}%")

# Fetch historical data from Binance
def fetch_klines(symbol, interval, start_str, end_str=None):
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return df

# Main function
def main():
    symbol = 'BTCUSDT'
    interval = '1d'
    start_str = '1 Jan 2021'
    end_str = '1 Jan 2022'
    df = fetch_klines(symbol, interval, start_str, end_str)
    signals = signal_generation(df, bollinger_bands)
    new = copy.deepcopy(signals)
    plot(new)
    backtest_strategy(new)

if __name__ == '__main__':
    main()
