import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from binance.client import Client
from binance.enums import HistoricalKlinesType
from binance import ThreadedWebsocketManager
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import os

# Initialize Binance client
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')
client = Client(api_key, api_secret)

# Global variables to hold the moving averages and other parameters
ma1 = 12
ma2 = 26
ticker = 'MATICUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE


# Simple moving average
def macd(signals, ma1, ma2):
    signals['ma1'] = signals['Close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['Close'].rolling(window=ma2, min_periods=1, center=False).mean()
    return signals


# Feature engineering
def feature_engineering(df):
    df = macd(df, ma1, ma2)
    df['returns'] = df['Close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=10).std()
    df['momentum'] = df['returns'].rolling(window=10).sum()
    df['signal'] = np.where(df['ma1'] > df['ma2'], 1, 0)
    return df.dropna()


# Fetch historical data from Binance
def fetch_binance_data(ticker, start_date, end_date, interval):
    klines = client.get_historical_klines(ticker, interval, start_date, end_date,
                                          klines_type=HistoricalKlinesType.FUTURES)
    data = pd.DataFrame(klines, columns=[
        'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time',
        'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base_asset_volume',
        'Taker_buy_quote_asset_volume', 'Ignore'
    ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return data


# Split data into training and testing sets
def split_data(df):
    X = df[['ma1', 'ma2', 'returns', 'volatility', 'momentum']]
    y = df['signal']
    return train_test_split(X, y, test_size=0.2, random_state=42)


# Train the machine learning model
def train_model(X_train, y_train):
    if len(X_train) == 0 or len(y_train) == 0:
        raise ValueError("Training data is empty. Check your data preprocessing steps.")

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, "macd_model.pkl")
    return model


# Evaluate the model
def evaluate_model(model, X_test, y_test):
    if len(X_test) == 0 or len(y_test) == 0:
        raise ValueError("Testing data is empty. Check your data preprocessing steps.")

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")


# Main function to fetch data, train the model, and evaluate it
def main():
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    # Fetch historical data
    df = fetch_binance_data(ticker, start_date, end_date, interval)
    df = feature_engineering(df)

    # Split data
    X_train, X_test, y_train, y_test = split_data(df)

    # Train model
    model = train_model(X_train, y_train)

    # Evaluate model
    evaluate_model(model, X_test, y_test)

    # Start WebSocket manager for real-time predictions
    # twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    # twm.start()
    # twm.start_kline_socket(callback=lambda msg: process_message(msg, model), symbol=ticker, interval=interval)

    # Keep the script running
    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     twm.stop()


# Process message from WebSocket
def process_message(msg, model):
    new_data = [msg['E'], msg['k']['o'], msg['k']['h'], msg['k']['l'], msg['k']['c'], msg['k']['v']]
    new_df = pd.DataFrame([new_data], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
    new_df.set_index('timestamp', inplace=True)
    new_df = new_df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    new_df = feature_engineering(new_df)

    if not new_df.empty:
        features = new_df[['ma1', 'ma2', 'returns', 'volatility', 'momentum']]
        prediction = model.predict(features)
        signal = "Buy" if prediction[-1] == 1 else "Sell"

        print(f"Timestamp: {new_df.index[-1]}, Close: {new_df['Close'].iloc[-1]}, Signal: {signal}")
    else:
        print("New data frame is empty after feature engineering.")


if __name__ == '__main__':
    main()
