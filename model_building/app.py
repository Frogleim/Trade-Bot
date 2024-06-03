from flask import Flask, send_file
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import ccxt
import pandas as pd
import plotly.graph_objs as go
import io
import numpy as np


# Function to fetch OHLCV data from Binance
def fetch_ohlcv(symbol='MATIC/USDT', timeframe='15m', limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


# Backtest function with take profit and stop loss
def backtest(signals, capital, take_profit, stop_loss):
    positions = []
    balance = capital
    btc_balance = 0
    entry_price = 0
    for i in range(len(signals)):
        if signals['signals'][i] == 1 and btc_balance == 0:  # Buy signal
            btc_balance = balance / signals['close'][i]
            balance = 0
            entry_price = signals['close'][i]
            positions.append(('Buy', signals.index[i], signals['close'][i], btc_balance))
        elif btc_balance > 0:
            price_change = (signals['close'][i] - entry_price) / entry_price
            if price_change >= take_profit or price_change <= stop_loss:
                balance = btc_balance * signals['close'][i]
                btc_balance = 0
                positions.append(('Sell', signals.index[i], signals['close'][i], balance))
    return positions, balance


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
app = Dash(__name__, server=server, url_base_pathname='/')

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
    positions, _ = backtest(signals, 100, 0.0060, -0.0045)
    print(positions)
    buys = [pos for pos in positions if pos[0] == 'Buy']
    sells = [pos for pos in positions if pos[0] == 'Sell']

    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlesticks'
    )])

    last_candle = df.iloc[-1]

    if buys:
        fig.add_trace(go.Scatter(
            x=[last_candle['timestamp']],
            y=[last_candle['close']],
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=15),
            name='Buy'
        ))

    if sells:
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
        xaxis_rangeslider_visible=False
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)
