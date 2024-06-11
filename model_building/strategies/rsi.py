import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client

# Set your API key and secret
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'

client = Client(API_KEY, API_SECRET)

def smma(series, n):
    output = [series[0]]
    for i in range(1, len(series)):
        temp = output[-1] * (n - 1) + series[i]
        output.append(temp / n)
    return output

def rsi(data, n=14):
    delta = data.diff().dropna()
    up = np.where(delta > 0, delta, 0)
    down = np.where(delta < 0, -delta, 0)
    rs = np.divide(smma(up, n), smma(down, n))
    output = 100 - 100 / (1 + rs)
    return output[n - 1:]

def signal_generation(df, method, n=14):
    df['rsi'] = 0.0
    df['rsi'][n:] = method(df['Close'], n=14)
    df['positions'] = np.select([df['rsi'] < 30, df['rsi'] > 70], [1, -1], default=0)
    df['signals'] = df['positions'].diff()
    return df[n:]

def plot(new, ticker):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(211)
    new['Close'].plot(label=ticker)
    ax.plot(new.loc[new['signals'] == 1].index, new['Close'][new['signals'] == 1], label='LONG', lw=0, marker='^', c='g')
    ax.plot(new.loc[new['signals'] == -1].index, new['Close'][new['signals'] == -1], label='SHORT', lw=0, marker='v', c='r')
    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Positions')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()

    bx = plt.figure(figsize=(10, 10)).add_subplot(212, sharex=ax)
    new['rsi'].plot(label='Relative Strength Index', c='#522e75')
    bx.fill_between(new.index, 30, 70, alpha=0.5, color='#f22f08')
    bx.text(new.index[-45], 75, 'Overbought', color='#594346', size=12.5)
    bx.text(new.index[-45], 25, 'Oversold', color='#594346', size=12.5)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('RSI')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

def fetch_klines(symbol, interval, start_str, end_str=None):
    klines = client.futures_historical_klines(symbol, interval, start_str, end_str)
    df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return df

def backtest_strategy(df):
    initial_balance = 1000  # Initial balance in USDT
    balance = initial_balance
    position = 0  # Positive for long, negative for short
    position_size = 0.01  # Size of each position (0.01 BTC)
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

def main():
    symbol = 'BTCUSDT'
    interval = '1d'
    start_str = '1 Jan 2023'
    end_str = '1 Jan 2024'
    df = fetch_klines(symbol, interval, start_str, end_str)
    new = signal_generation(df, rsi, n=14)
    plot(new, symbol)
    backtest_strategy(new)

if __name__ == '__main__':
    main()
