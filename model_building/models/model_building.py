import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

# Load your historical data
df = pd.read_csv('./historical_data/MATICUSDT_15min_data.csv')

# Feature engineering: add technical indicators (e.g., moving averages, RSI, etc.)
df['SMA'] = df['close'].rolling(window=14).mean()
df['EMA'] = df['close'].ewm(span=14, adjust=False).mean()
# Add more features as needed

# Drop rows with NaN values from the entire DataFrame
df.dropna(inplace=True)

# Prepare the data
X = df[['open', 'high', 'low', 'volume', 'SMA', 'EMA']]
y = df['close'].shift(-1).dropna()

# Ensure that X and y have the same length after processing
X = X.loc[y.index]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print('Mean Squared Error:', mse)

# Save the model
joblib.dump(model, 'model.pkl')
