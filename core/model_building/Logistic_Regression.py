import pandas as pd
import numpy as np
from binance.client import Client
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import datetime

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

client = Client(api_key, api_secret)

def get_historical_data(symbol, interval, start_str, end_str=None):
    print('Getting data from Binance...')
    klines = client.futures_historical_klines(symbol, interval, start_str, end_str)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data = data.astype(float)
    print('Data got successfully...')
    return data

symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 Jan 2021'

data = get_historical_data(symbol, interval, start_str)

def add_features(data):
    print('Adding features...')
    data['return'] = data['close'].pct_change()
    data['sma_5'] = data['close'].rolling(window=5).mean()
    data['sma_10'] = data['close'].rolling(window=10).mean()
    data['ema_5'] = data['close'].ewm(span=5).mean()
    data['ema_10'] = data['close'].ewm(span=10).mean()
    data['volatility'] = data['close'].rolling(window=10).std()
    data['future_close'] = data['close'].shift(-1)
    data.dropna(inplace=True)
    print('Features added successfully')
    return data

data = add_features(data)

print('Preparing train data...')
features = ['return', 'sma_5', 'sma_10', 'ema_5', 'ema_10', 'volatility']
X = data[features]
y = data['future_close']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse:.2f}')

data['predicted_close'] = model.predict(data[features])

# Display the latest predictions
print(data[['close', 'predicted_close']].tail())
