import pandas as pd
import numpy as np
from binance.client import Client

client = Client(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET')
def calculate_ema(prices, window):
    return prices.ewm(span=window, adjust=False).mean()


def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def generate_signal(df):
    close = df['close']
    ema_short = calculate_ema(close, 12)
    ema_long = calculate_ema(close, 26)
    rsi = calculate_rsi(close, 14)

    # Calculate MACD and the Signal Line
    macd = ema_short - ema_long
    signal_line = calculate_ema(macd, 9)

    # Decision rule: Buy if MACD crosses above the signal line, Sell if it crosses below
    if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] < signal_line.iloc[-2]:
        return "Buy", close.iloc[-1]
    elif macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] > signal_line.iloc[-2]:
        return "Sell", close.iloc[-1]
    else:
        return "Hold", close.iloc[-1]


def get_latest_candlestick(symbol):
    candles = client.futures_klines(symbol=symbol, interval='5m', limit=500)
    df = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df


def backtest_strategy(df, capital, risk_per_trade, stop_loss_pct, take_profit_pct):
    cash = capital
    position_size = 0
    entry_price = 0
    profit = 0

    results = []

    for index, row in df.iterrows():
        current_price = row['close']
        signal = generate_signal(df.loc[:index])

        if signal[0] == 'Buy' and cash > 0:
            # Calculate number of shares to buy
            position_size = (cash * risk_per_trade) / current_price
            entry_price = current_price
            cash -= position_size * entry_price
            results.append((index, 'Buy', entry_price, position_size, cash, 0))  # No profit on buying

        elif position_size > 0:
            # Calculate stop loss and take profit prices
            stop_loss_price = entry_price * (1 - stop_loss_pct)
            take_profit_price = entry_price * (1 + take_profit_pct)

            if current_price <= stop_loss_price or current_price >= take_profit_price:
                cash += position_size * current_price
                profit = (current_price - entry_price) * position_size  # Calculate profit
                results.append((index, 'Sell', current_price, position_size, cash, profit))
                position_size = 0  # Reset position
                entry_price = 0

    return pd.DataFrame(results, columns=['Date', 'Action', 'Price', 'Position Size', 'Cash', 'Profit'])

if __name__ == '__main__':
    symbol = 'MATICUSDT'
    df = get_latest_candlestick(symbol)
    capital = 35
    risk_per_trade = 0.01
    stop_loss_pct = 0.50
    take_profit_pct = 0.80
    result = backtest_strategy(df, capital, risk_per_trade, stop_loss_pct, take_profit_pct)
    print(result)