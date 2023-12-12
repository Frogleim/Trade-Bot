import pandas as pd
import numpy as np
from binance.client import Client
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import pickle
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
print(grandparent_dir)
files_dir = os.path.join(grandparent_dir, "core/trade")


def get_historical_data():
    api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'

    api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
    client = Client(api_key, api_secret)
    interval = '15m'
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


def train_base_model():
    df = get_historical_data()
    # Assuming df is your DataFrame
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Feature Scaling
    scaler_filename = f'{files_dir}/model/minmax_scaler.pkl'
    try:
        # Load existing scaler
        with open(scaler_filename, 'rb') as scaler_file:
            scaler = pickle.load(scaler_file)
    except FileNotFoundError:
        # Create a new scaler if not found
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
    with open(scaler_filename, 'wb') as scaler_file:
        pickle.dump(scaler, scaler_file)
    model.save(f'{files_dir}/model/trade_model_1min.h5')


if __name__ == '__main__':
    train_base_model()