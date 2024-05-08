from binance.client import Client
import pandas as pd
import datetime

api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Initialize the Binance client
client = Client(api_key, api_secret)


def fetch_data(symbol, interval, lookback):
    # Calculate the timestamps for the lookback period
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=lookback)

    # Convert to milliseconds
    start_ts = int(start_time.timestamp() * 1000)
    end_ts = int(end_time.timestamp() * 1000)

    # Container for all fetched data
    all_candles = []

    # Fetch data in a loop until all candles from the lookback period are fetched
    while True:
        candles = client.futures_klines(symbol=symbol, interval=interval, startTime=start_ts, endTime=end_ts,
                                        limit=1000)
        if not candles:
            break
        all_candles += candles
        # Update start_ts to last fetched candle's close time + 1 ms to avoid overlapping
        start_ts = candles[-1][0] + 1

    # Create a DataFrame
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume',
               'close_time', 'quote_asset_volume', 'number_of_trades',
               'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(all_candles, columns=columns)

    # Convert timestamp to readable date
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

    # Convert columns to appropriate data types
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    return df


# Fetch 3 years of hourly data
df = fetch_data('MATICUSDT', Client.KLINE_INTERVAL_1HOUR, lookback=365 * 3)

# Print and save the data
print(df.head())
df.to_csv('MATICUSDT_hourly_data_3_years.csv', index=False)
