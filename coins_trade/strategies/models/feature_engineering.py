import pandas as pd
import talib
from sklearn.preprocessing import StandardScaler

def apply_feature_engineering(df):
    df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
    df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
    df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
    df['open_time'] = pd.to_datetime(df['open_time']).astype('int64') // 10**9
    df['close_time'] = pd.to_datetime(df['close_time']).astype('int64') // 10**9
    scaler = StandardScaler()
    columns_to_scale = ['open', 'high', 'low', 'close', 'volume', 'sma_50', 'ema_50', 'rsi', 'macd', 'macd_signal', 'macd_hist']
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    
    
    for i in range(1, 2):
        df[f'close_lag_{i}'] = df['close'].shift(i)
    
    df.dropna(inplace=True)
    
    return df


if __name__ == '__main__':
    df = pd.read_csv('data/MATICUSDT_hourly_data_3_years.csv')
    df = apply_feature_engineering(df)
    df.to_csv('./data/MATICUSDT_feature.csv', index=False)
