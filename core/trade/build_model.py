from binance.client import Client
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
# import matplotlib.pyplot as plt


def calculate_demark_trendline(close_prices, periods=5):
    demark_trendline = close_prices.rolling(window=periods, min_periods=1).mean()
    return demark_trendline


def historical_data():
    api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'

    api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
    client = Client(api_key, api_secret)
    interval = '1h'
    symbol = 'ETHUSDT'
    n = 200
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=n)
    timestamps = [int(kline[0]) for kline in klines]
    open_prices = [float(kline[1]) for kline in klines]
    high_prices = [float(kline[2]) for kline in klines]
    low_prices = [float(kline[3]) for kline in klines]
    close_prices = [float(kline[4]) for kline in klines]
    date = pd.to_datetime(timestamps, unit='ms')

    # Create a DataFrame with DatetimeIndex
    df = pd.DataFrame({
        'date': date,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
    }, index=pd.to_datetime(timestamps, unit='ms'))
    return df


def train_model():
    df = historical_data()
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Feature Scaling
    scaler = MinMaxScaler()
    df[['open', 'high', 'low', 'close']] = scaler.fit_transform(df[['open', 'high', 'low', 'close']])

    # Train-Test Split
    X = df[['open', 'high', 'low', 'close']]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build the model
    model = Sequential()
    model.add(Dense(128, input_dim=X_train.shape[1], activation='relu'))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(Dense(64, activation='relu'))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(Dense(32, activation='relu'))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(Dense(1, activation='sigmoid'))

    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)  # You can adjust the learning rate
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=900, batch_size=200, validation_data=(X_test, y_test))

    # Evaluate the model
    loss, accuracy = model.evaluate(X_test, y_test)
    print("Accuracy:", accuracy)

    # Assuming new_data is your new DataFrame with similar structure
    df[['open', 'high', 'low', 'close']] = scaler.transform(df[['open', 'high', 'low', 'close']])
    df['predicted_target'] = np.round(model.predict(df[['open', 'high', 'low', 'close']])).astype(int)
    df['predicted_prob'] = model.predict(X)
    threshold = 0.5  # You can adjust this threshold based on your strategy
    df['trading_signal'] = np.where(df['predicted_prob'] > threshold, 1, -1)

    # Print or visualize the trading signals
    pd.set_option('display.max_rows', None)

    return df, model

