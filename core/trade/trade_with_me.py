import pandas as pd
import numpy as np
from binance.client import Client
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import pickle
import sys
import logging
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
print(grandparent_dir)
files_dir = os.path.join(grandparent_dir, "core/trade")
log_dir = os.path.join(grandparent_dir, "Trade-Bot")
print(log_dir)
logging.basicConfig(filename=f'{grandparent_dir}/logs/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
error_handler = logging.FileHandler(f'{grandparent_dir}/logs/error_logs.log')
error_handler.setLevel(logging.ERROR)  # Set the desired log level for the file
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
error_console_handler = logging.StreamHandler(sys.stdout)
error_console_handler.setLevel(logging.ERROR)  # Set the desired log level for the console
error_console_handler.setFormatter(error_formatter)
error_logger.addHandler(error_console_handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


def get_historical_data():
    api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
    api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
    client = Client(api_key, api_secret)
    interval = '1h'
    symbol = 'ETHUSDT'
    n = 10
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


def predict_crypto():
    """

    Returns: predicted dataframe

    """
    new_data = get_historical_data()
    loaded_model = tf.keras.models.load_model(f'{files_dir}/model/trade_model_1hrs.h5')
    scaler_filename = f'{files_dir}/model/minmax_scaler.pkl'

    try:
        # Load existing scaler
        with open(scaler_filename, 'rb') as scaler_file:
            scaler = pickle.load(scaler_file)
    except FileNotFoundError:
        # Create a new scaler if not found
        scaler = MinMaxScaler()
    new_data[['open', 'high', 'low', 'close']] = scaler.transform(new_data[['open', 'high', 'low', 'close']])

    X_new = new_data[['open', 'high', 'low', 'close']]
    y_new = (new_data['close'].shift(-1) > new_data['close']).astype(int)
    X_train_new, X_test_new, y_train_new, y_test_new = train_test_split(X_new, y_new, test_size=0.2, random_state=42)
    loaded_model.fit(X_train_new, y_train_new, epochs=45, batch_size=10, validation_data=(X_test_new, y_test_new))
    new_data['predicted_prob'] = loaded_model.predict(X_new)
    threshold = 0.5
    new_data['trading_signal'] = np.where(new_data['predicted_prob'] > threshold, 1, -1)
    loaded_model.save('./model/trade_model_1hrs.h5')
    res = new_data[['close', 'predicted_prob', 'trading_signal']].iloc[-1]
    logging.info(res)

    return res


if __name__ == '__main__':
    new_data = predict_crypto()
    print(round(new_data['predicted_prob'] * 100))