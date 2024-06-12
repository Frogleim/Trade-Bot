from flask import Flask, render_template_string, render_template
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from model_building.strategies import patterns, BB, MACD
from db import DataBase
from binance.client import Client

api_key = 'Gt9HDhbJu5GC5yFkGcL42KAeLx28ISQJ8GxMFU7mG3KwZwCAcXEeiwhOOdOkvDUi'
api_secret = '6CXlH9wGvvpeyI1h8zWW2nlgAfp0bBRcmkjLxNUtzMBlIOgYBVsv5oNc9SkagpQw'
my_db = DataBase()
server = Flask(__name__)
app = Dash(__name__, server=server, url_base_pathname='/chart/')
client = Client(api_key, api_secret)


def get_account_info():
    data = client.futures_account()
    avail_balance = data['availableBalance']
    trades = client.futures_account_trades()
    return avail_balance, trades


@server.route("/account")
def account():
    balance, trades = get_account_info()
    return render_template("account.html", balance=balance, trades=trades)


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
    df = MACD.fetch_ohlcv()
    signals = MACD.generate_signals(df)
    signal = signals['signals'].iloc[-1]
    bol_signal, bol_price = BB.check_sma()
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

    if signal > 0 or bol_signal == 'Buy':
        my_db.insert_trades(symbol='MATICUSDT', signal='Buy', entry_price=bol_price)
        fig.add_trace(go.Scatter(
            x=[last_candle['timestamp']],
            y=[last_candle['close']],
            mode='markers',
            marker=dict(symbol='triangle-up', color='green', size=15),
            name='Buy'
        ))

    if signal < 0 or bol_signal == 'Sell':
        my_db.insert_trades(symbol='MATICUSDT', signal='Sell', entry_price=bol_price)
        fig.add_trace(go.Scatter(
            x=[last_candle['timestamp']],
            y=[last_candle['close']],
            mode='markers',
            marker=dict(symbol='triangle-down', color='red', size=15),
            name='Sell'
        ))

    if signal == 0.0:
        my_db.clean_db()
        print('Cleaning database')

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
    app.run(host='0.0.0.0', port=5050, debug=True)
