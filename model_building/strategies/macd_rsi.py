from binance.client import Client
import pandas as pd
import numpy as np

client = Client()

def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df['EMA12'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    return df


def calculate_rsi(df, period=14):
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df


def get_signals(df):
    df = calculate_macd(df)
    df = calculate_rsi(df)

    buy_signals = (df['MACD'] > df['Signal Line']) & (df['RSI'] < 30)
    sell_signals = (df['MACD'] < df['Signal Line']) & (df['RSI'] > 70)

    df['Buy Signal'] = np.where(buy_signals, 1, 0)
    df['Sell Signal'] = np.where(sell_signals, 1, 0)
    return df


# Example data
data = {
    'timestamp': pd.date_range(start='2023-01-01', periods=100),
    'close': np.random.random(100) * 100
}
df = pd.DataFrame(data)

# Calculate signals
df = get_signals(df)

# Display the resulting dataframe with signals
print(df[['timestamp', 'close', 'MACD', 'Signal Line', 'RSI', 'Buy Signal', 'Sell Signal']])