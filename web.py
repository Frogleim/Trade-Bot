from flask import Flask, render_template_string
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import ccxt
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from model_building.strategies import patterns
from db import DataBase

my_db = DataBase()


# Function to fetch OHLCV data from Binance
def fetch_ohlcv(symbol='MATIC/USDT', timeframe='15m', limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def generate_signals(df):
    ma1 = 12
    ma2 = 26
    signals = df.copy()
    signals['ma1'] = signals['close'].rolling(window=ma1, min_periods=1, center=False).mean()
    signals['ma2'] = signals['close'].rolling(window=ma2, min_periods=1, center=False).mean()
    signals['positions'] = 0
    signals['positions'][ma1:] = np.where(signals['ma1'][ma1:] >= signals['ma2'][ma1:], 1, 0)
    signals['signals'] = signals['positions'].diff()
    signals['oscillator'] = signals['ma1'] - signals['ma2']
    return signals


# Create Flask server
server = Flask(__name__)

# Create Dash app
app = Dash(__name__, server=server, url_base_pathname='/chart/')

app.layout = html.Div([
    html.H1("MATIC/USDT Live Candlestick Chart"),
    dcc.Graph(id='live-candlestick-chart'),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # Update every 15 minutes
        n_intervals=0
    )
])


@app.callback(Output('live-candlestick-chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_chart(n):
    df = fetch_ohlcv()
    signals = generate_signals(df)
    signal = signals['signals'].iloc[-1]
    print(f"Signal: {signal}")
    patterns_signal = patterns.detect_head_shoulder(df)
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlesticks'
    )])

    last_candle = df.iloc[-1]
    print(patterns_signal['head_shoulder_pattern'].iloc[-1])
    position_closed_text = ""

    if patterns_signal['head_shoulder_pattern'].iloc[-1] == 'Head and Shoulder':
        pass

    if signal > 0:
        entry_price = last_candle['close']
        my_db.insert_trades(symbol='MATICUSDT', signal='Buy', entry_price=entry_price)
        fig.add_trace(go.Scatter(
            x=[last_candle['timestamp']],
            y=[last_candle['close']],
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=15),
            name='Buy'
        ))

    if signal < 0:
        entry_price = last_candle['close']
        my_db.insert_trades(symbol='MATICUSDT', signal='Sell', entry_price=entry_price)
        fig.add_trace(go.Scatter(
            x=[last_candle['timestamp']],
            y=[last_candle['close']],
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=15),
            name='Sell'
        ))

    fig.update_layout(
        title='MATIC/USDT Live Candlestick Chart',
        xaxis_title='Time',
        yaxis_title='Price (USDT)',
        xaxis_rangeslider_visible=False,
        annotations=[go.layout.Annotation(
            xref='paper',
            yref='paper',
            x=0.5,
            y=0,
            showarrow=False,
            text=position_closed_text,
            font=dict(
                size=12,
                color="black"
            ),
            align="center"
        )] if position_closed_text else []
    )
    return fig


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
