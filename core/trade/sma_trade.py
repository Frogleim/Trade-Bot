import pandas as pd
import pandas_ta as ta
from binance.client import Client
from profitable_exit_strategy import pnl_short, pnl_long


api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

client = Client(api_key, api_secret)
symbol = 'ETHUSDT'


def get_sma():
    interval = '15m'
    klines = client.futures_klines(symbol=symbol, interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    length = 20
    df['sma'] = ta.sma(df['close'], length=length)
    sma_value = df['sma'].iloc[-1]
    return sma_value


def get_live_price():
    live_price = client.futures_ticker(symbol=symbol)['lastPrice']
    return live_price


def check_signal():
    sma = get_sma()
    live_price = get_live_price()
    print(f'Live price: {live_price} --- SMA: {round(float(sma), 2)}')
    signal = float(live_price) - float(sma)
    if 0 <= signal <= 3:
        print(f'Placing Buy Order\nEntry Price: {live_price}\nSMA: {sma}')
        while True:
            res = pnl_long(live_price, sma)
            if res == 'Profit':
                break
            if res == 'Loss':
                break
    if 0 >= signal >= -3:
        print(f'Placing Sell Order\nEntry Price: {live_price}\nSMA: {sma}')
        while True:
            res = pnl_short(live_price, sma)
            if res == 'Profit':
                break
            if res == 'Loss':
                break


if __name__ == '__main__':
    while True:
        check_signal()
