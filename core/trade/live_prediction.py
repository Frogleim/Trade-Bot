from build_model import train_base_model
from binance.client import Client
import time
import numpy as np
import pandas as pd


def get_live_data(api_key, api_secret, symbol='ETHUSDT', interval='15m', limit=200):
    client = Client(api_key, api_secret)
    while True:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

        timestamps = [int(kline[0]) for kline in klines]
        open_prices = [float(kline[1]) for kline in klines]
        high_prices = [float(kline[2]) for kline in klines]
        low_prices = [float(kline[3]) for kline in klines]
        close_prices = [float(kline[4]) for kline in klines]
        date = pd.to_datetime(timestamps, unit='ms')

        df_live = pd.DataFrame({
            'date': date,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
        }, index=pd.to_datetime(timestamps, unit='ms'))

        yield df_live
        time.sleep(60)

def interpret_entry_point(entry_point):
    if entry_point == 1:
        return "Buy"
    elif entry_point == 0:
        return "Sell"
    else:
        return "Hold"  # Add additional logic as needed

def predict_live(model, scaler, live_data_generator):
    for live_df in live_data_generator:
        # Feature Scaling using the saved scaler
        live_df[['open', 'high', 'low', 'close']] = scaler.transform(live_df[['open', 'high', 'low', 'close']])

        # Extract features for prediction
        features = live_df[['open', 'high', 'low', 'close']]

        # Generate predictions
        predictions = model.predict(features)

        # Choose a threshold (you can adjust this based on your strategy)
        threshold = 0.5

        # Identify entry points based on the threshold
        entry_points = (predictions > threshold).astype(int)

        # Extract probabilities from the output layer
        probabilities = predictions[:, 0]  # Assuming your output layer has one neuron

        # Interpret entry points as "Buy" or "Sell"
        signals = np.where(entry_points == 1, "Buy", "Sell")

        # Add signals and probabilities to the DataFrame
        live_df['signal'] = signals
        live_df['probability'] = round(float(probabilities), 2) # Convert to percentage

        print(live_df[['date', 'open', 'close', 'signal', 'probability']])  # Print relevant information
        time.sleep(15*60)
        return live_df[['date', 'open', 'close', 'signal', 'probability']]


if __name__ == '__main__':

    import os
    import tensorflow as tf
    import pickle

    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    print(grandparent_dir)
    files_dir = os.path.join(grandparent_dir, "core/trade")
    api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
    api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'
    train_base_model()
    model = tf.keras.models.load_model(f'{files_dir}/model/trade_model_1min.h5')
    with open(f'{files_dir}/model/minmax_scaler.pkl', 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    live_data_generator = get_live_data(api_key, api_secret)
    df = predict_live(model, scaler, live_data_generator)
    last_four_signals = df['signal'].tail(4).tolist()

    if all(signal == last_four_signals[0] for signal in last_four_signals):
        print("The last four signals are the same:", last_four_signals[0])
    else:
        print("The last four signals are different.")