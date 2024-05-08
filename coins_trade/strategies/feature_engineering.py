import pandas as pd
import talib
from sklearn.preprocessing import StandardScaler

def read_data():
    df = pd.read_csv('MATICUSDT_hourly_data.csv')
    return df


df = read_data()
# Calculate SMA and EMA
df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
df['ema_50'] = talib.EMA(df['close'], timeperiod=50)

# Calculate RSI
df['rsi'] = talib.RSI(df['close'], timeperiod=14)

# Calculate MACD
df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
# Identifying Doji
df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])

# Identifying Hammer
df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])

# Identifying Engulfing Pattern
# TODO add another one pattern
# df['bullish_engulfing'] = talib.CDL(df['open'], df['high'], df['low'], df['close'])
# df['bearish_engulfing'] = talib.CDLBEARISHENGULFING(df['open'], df['high'], df['low'], df['close'])
scaler = StandardScaler()

# Select columns to scale
columns_to_scale = ['open', 'high', 'low', 'close', 'volume', 'sma_50', 'ema_50', 'rsi', 'macd', 'macd_signal', 'macd_hist']
df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])

for i in range(1, 2):
    df[f'close_lag_{i}'] = df['close'].shift(i)


df.dropna(inplace=True)  # Drop all rows with NaN values
print(df)
df.to_csv('./data/MATICUSDT_feature.csv', index=False)