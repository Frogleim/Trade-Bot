import pandas as pd
import matplotlib.pyplot as plt
import pickle
from sklearn.ensemble import RandomForestClassifier
from feature_engineering import apply_feature_engineering  # Assuming you have this function

# Load the trained model
model = pickle.load(open('./model/random_forest_model.sav', 'rb'))

# Load historical data
data = pd.read_csv('data/MATICUSDT_hourly_data_3_years.csv')
data['open_time'] = pd.to_datetime(data['open_time'])

# Apply the same feature engineering as during training
data = apply_feature_engineering(data)  # This function should encapsulate all your feature engineering steps

# Generate signals based on model prediction
# Exclude non-feature columns that were not used during model training
features = data.drop(columns=['label', 'open_time', 'close_time'], errors='ignore')  # Adjust based on actual feature columns
data['signal'] = model.predict(features)

# Calculate returns and strategy returns
data['returns'] = data['close'].pct_change()
data['strategy_returns'] = data['returns'] * data['signal'].shift(1)  # Shift signal to trade on next open

# Simulate trading
initial_capital = float(10000.0)
positions = pd.DataFrame(index=data.index).fillna(0.0)
positions['signal'] = data['signal']
positions['MATICUSDT'] = 100 * positions['signal']  # Buy 100 shares

# Initialize the portfolio with value owned
portfolio = positions.multiply(data['close'], axis=0)
pos_diff = positions.diff()
portfolio['holdings'] = (positions.multiply(data['close'], axis=0)).sum(axis=1)
portfolio['cash'] = initial_capital - (pos_diff.multiply(data['close'], axis=0)).sum(axis=1).cumsum()
portfolio['total'] = portfolio['cash'] + portfolio['holdings']
portfolio['returns'] = portfolio['total'].pct_change()

# Print the first few lines of the `portfolio`
print(portfolio.head())

# Plot the results
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')
portfolio['total'].plot(ax=ax1, color='r', lw=2.)
ax1.plot(portfolio.loc[positions['signal'] == 1.0].index,
         portfolio.total[positions['signal'] == 1.0],
         '^', markersize=10, color='m')
ax1.plot(portfolio.loc[positions['signal'] == 0.0].index,
         portfolio.total[positions['signal'] == 0.0],
         'v', markersize=10, color='k')
plt.show()
