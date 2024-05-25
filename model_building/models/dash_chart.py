from flask import Flask
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import ccxt
import pandas as pd
import plotly.graph_objs as go


# Function to fetch OHLCV data from Binance
def fetch_ohlcv(symbol='MATIC/USDT', timeframe='1m', limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


# Create Flask server
server = Flask(__name__)

# Create Dash app
app = Dash(__name__, server=server, url_base_pathname='/')

app.layout = html.Div([
    html.H1("MATIC/USDT Live Candlestick Chart"),
    dcc.Graph(id='live-candlestick-chart'),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # Update every minute
        n_intervals=0
    )
])


@app.callback(Output('live-candlestick-chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_chart(n):
    df = fetch_ohlcv()
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlesticks'
    )])

    fig.update_layout(
        title='MATIC/USDT Live Candlestick Chart',
        xaxis_title='Time',
        yaxis_title='Price (USDT)',
        xaxis_rangeslider_visible=False
    )
    return fig


if __name__ == '__main__':
    server.run(debug=True)
