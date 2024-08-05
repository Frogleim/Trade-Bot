import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from binance.client import Client
import pickle
import ta

# Load the model
with open('./models/model/ema_crossover_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

# Binance client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

def get_historical_data(symbol, interval, start_str):
    try:
        print('DataFrame already exists')
        data = pd.read_csv(f'./models/data/{symbol}_historical.csv')
        return data
    except FileNotFoundError:
        print('Getting historical data...')
        # Fetch historical data from Binance
        klines = client.get_historical_klines(symbol, interval, start_str)
        data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                            'close_time', 'quote_asset_volume', 'number_of_trades', 
                                            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        data = data[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data[['open', 'high', 'low', 'close', 'volume']] = data[['open', 'high', 'low', 'close', 'volume']].astype(float)
        data.to_csv(f'./models/data/{symbol}_historical.csv')
        return data

# Compute EMAs
symbol = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 Jan 2020'
data = get_historical_data(symbol, interval, start_str)

# Debugging: Print the first few rows of data
print("Data Head:")
print(data.head())

def compute_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

atr_period = 14
data['ema_short'] = compute_ema(data['close'], span=5)
data['ema_long'] = compute_ema(data['close'], span=8)
data['ATR'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], window=atr_period)

# Check for missing values
print(data.isna().sum())

# Debugging prints
print("EMA Short Head:")
print(data['ema_short'].head())

print("EMA Long Head:")
print(data['ema_long'].head())

print("ATR Head:")
print(data['ATR'].head())

# Prepare features for prediction
features = ['ema_short', 'ema_long', 'ATR']
data = data.dropna(subset=features)  # Ensure no NaN values in features

# Debugging: Print the shape of the data
print("Data Shape after dropping NaNs:", data.shape)

data['signal'] = loaded_model.predict(data[features])

# Debugging print for signals
print("Signals Distribution:")
print(data['signal'].value_counts())

# Backtesting
initial_balance = 100.0
balance = initial_balance
position = 0  # 0 means no position, 1 means holding the asset
entry_price = 0
trade_log = []

for i in range(len(data)):
    signal = data.iloc[i]['signal']
    price = data.iloc[i]['close']
    
    if signal == 1 and position == 0:
        # Buy signal
        position = balance / price
        entry_price = price
        balance = 0
        trade_log.append(('Buy', data.iloc[i]['timestamp'], price, position))
    
    elif signal == -1 and position > 0:
        # Sell signal
        balance = position * price
        position = 0
        trade_log.append(('Sell', data.iloc[i]['timestamp'], price, balance))

# If still holding a position at the end, sell it
if position > 0:
    balance = position * data.iloc[-1]['close']
    trade_log.append(('Sell', data.iloc[-1]['timestamp'], data.iloc[-1]['close'], balance))

print(f"Final balance: ${balance:.2f}")

# Analyze results
trade_df = pd.DataFrame(trade_log, columns=['Action', 'Timestamp', 'Price', 'Balance/Position'])
print(trade_df)

# Calculate metrics
final_balance = balance
net_profit = final_balance - initial_balance
print(f"Net Profit: ${net_profit:.2f}")
print(f"Return on Investment (ROI): {net_profit / initial_balance * 100:.2f}%")

# Plot the results (optional)
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 7))
plt.plot(data['timestamp'], data['close'], label='Price')
buy_signals = trade_df[trade_df['Action'] == 'Buy']
sell_signals = trade_df[trade_df['Action'] == 'Sell']

plt.scatter(buy_signals['Timestamp'], buy_signals['Price'], marker='^', color='g', label='Buy', s=100)
plt.scatter(sell_signals['Timestamp'], sell_signals['Price'], marker='v', color='r', label='Sell', s=100)

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Backtest Trading Signals')
plt.legend()
plt.show()
