import joblib
import pandas as pd
from binance.client import Client
from sklearn.ensemble import RandomForestRegressor
import schedule
import time
from datetime import datetime

# Load the saved model
model = joblib.load('model.pkl')

# Initialize the Binance client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)


# Function to fetch live data from Binance API
def fetch_live_data():
    klines = client.get_klines(symbol='MATICUSDT', interval=Client.KLINE_INTERVAL_15MINUTE, limit=15)

    # Create a DataFrame
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
               'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(klines, columns=columns)

    # Convert columns to appropriate data types
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    return df


# Function to prepare data and make a prediction
def make_prediction():
    # Fetch live data
    live_data = fetch_live_data()

    # Calculate technical indicators for live data
    live_data['SMA'] = live_data['close'].rolling(window=14).mean()
    live_data['EMA'] = live_data['close'].ewm(span=14, adjust=False).mean()

    # Ensure no NaN values (drop the initial rows with NaN values due to indicator calculations)
    live_data.dropna(inplace=True)

    # Prepare the input for the model (using the latest data point)
    latest_data = live_data[['open', 'high', 'low', 'volume', 'SMA', 'EMA']].iloc[-1].values.reshape(1, -1)

    # Make a prediction
    prediction = model.predict(latest_data)[0]

    # Get the current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the prediction to a text file
    with open("predictions.txt", "a") as file:
        file.write(f"{current_time}, Predicted next close price: {prediction}\n")

    print(f"{current_time}, Predicted next close price: {prediction}")


# Schedule the prediction to run every 15 minutes
schedule.every().hour.at(":00").do(make_prediction)
schedule.every().hour.at(":15").do(make_prediction)
schedule.every().hour.at(":30").do(make_prediction)
schedule.every().hour.at(":45").do(make_prediction)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
