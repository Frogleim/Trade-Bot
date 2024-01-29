import pandas as pd
from binance.client import Client
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sideways import sideways_market_strategy
import time
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(parent_dir, "bot")

print(files_dir)
def read_config_json():
    with open(f'{files_dir}/config.json', "r") as f:
        data = json.load(f)
    print(data)
    return data






def get_realtime_data(symbol, interval):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=1)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']] = df[['open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']].apply(pd.to_numeric, errors='coerce')
    df.set_index('timestamp', inplace=True)
    return df

# Function to update chart with new data
def update_chart(fig, data, signals):
    # Clear previous data
    fig.data = []

    # Update candlestick chart
    candle = go.Candlestick(x=data.index, open=data['open'], high=data['high'], low=data['low'], close=data['close'], name='Candlestick')
    fig.add_trace(candle)

    # Update signals
    for signal in signals:
        action, timestamp, price = signal
        marker = dict(symbol='triangle-up' if action == 'Long' else 'triangle-down', size=10, color='green' if action == 'Long' else 'red')
        fig.add_trace(go.Scatter(x=[timestamp], y=[price], mode='markers', marker=marker, name=f'{action} Signal'))


if __name__ == '__main__':
    data = read_config_json()

    client = Client(data['keys']['api_key'], data['keys']['api_secret'])

    symbol = data['trade_config']['trading_pairs'][0]
    interval = data['trade_config']['interval']
    print(symbol, interval)
    initial_data = get_realtime_data(symbol, interval)
    initial_signals = sideways_market_strategy(initial_data)
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, subplot_titles=[f'{symbol} Live Chart'])
    update_chart(fig, initial_data, initial_signals)
    while True:
        real_time_data = get_realtime_data(symbol, interval)
        real_time_signals = sideways_market_strategy(real_time_data)
        update_chart(fig, real_time_data, real_time_signals)
        time.sleep(15)
