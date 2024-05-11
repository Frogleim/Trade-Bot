import pandas as pd
import pickle
import matplotlib.pyplot as plt

# Load the trained model
model = pickle.load(open('./model/random_forest_model.sav', 'rb'))

# Load the historical data
data = pd.read_csv('./data/MATICUSDT_feature.csv')
data['open_time'] = pd.to_datetime(data['open_time']).astype('int64') // 10**9
data['close_time'] = pd.to_datetime(data['close_time']).astype('int64') // 10**9

# Apply feature engineering (ensure this is identical to training setup)
# Assuming the function apply_feature_engineering is defined properly and includes all necessary transformations
# data = apply_feature_engineering(data)

# Check your actual feature names used in the model
# Here you need to ensure that only the columns used during training are included
# Example features might be: ['open_time', 'close_time', 'some_other_features_used_in_training']
# Replace 'some_other_features_used_in_training' with actual feature names from your model training
features = data[['open_time', 'close_time']]  # Adjust according to your actual feature set

# Predict using the model
data['signal'] = model.predict(data)
print(data['signal'])
# Simple trading strategy
data['position'] = data['signal'].shift(1)  # shift signals to simulate trading on the next open
data['market_return'] = data['close'].pct_change()
data['strategy_return'] = data['position'] * data['market_return']

# Calculate cumulative returns
data['cumulative_market_returns'] = (1 + data['market_return']).cumprod() - 1
data['cumulative_strategy_returns'] = (1 + data['strategy_return']).cumprod() - 1

# Plot results
plt.figure(figsize=(14, 7))
plt.plot(data['cumulative_market_returns'], label='Market Returns')
plt.plot(data['cumulative_strategy_returns'], label='Strategy Returns')
plt.title('Backtest Results')
plt.legend()
plt.show()
