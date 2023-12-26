import pandas as pd
from binance.client import Client
from profitable_exit_strategy import pnl_short, pnl_long
from files_manager import insert_data

# Define trading parameters
symbol: str = 'ETHUSDT'
interval = '15min'
initial_balance = 0.4  # Starting with $1
profit_target = 122  # Target $10 profit
client = Client()


def get_historical_klines(symbol, interval, limit=1000):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


# Function to calculate simple moving average (SMA)
def calculate_sma(df, window=9):
    df['close'] = pd.to_numeric(df['close'], errors='coerce')  # Convert 'close' to numeric
    df['sma'] = df['close'].rolling(window=window).mean()
    df = df.dropna()  # Drop rows with missing values
    return df


# Function to simulate a market order to buy
def simulate_buy(price, balance):
    quantity = balance / price
    return quantity


# Function to simulate a market order to sell
def simulate_sell(price, quantity):
    return quantity * price


# Function to backtest the trading strategy
def backtest_strategy(data):
    balance = initial_balance
    data = calculate_sma(data)

    in_position = False
    profit = 0
    num_trades = 0  # Initialize the number of trades counter

    # Initialize empty lists for buy and sell signals
    buy_signals = []
    sell_signals = []

    # Use the first timestamp as the start date
    start_date = data['timestamp'].iloc[0]
    print(start_date)

    for i in range(20, len(data)):
        if data['close'][i] > data['sma'][i] and not in_position:
            print(data['sma'][i])
            # Buy signal
            # buy_price = float(data['close'][i])
            # in_position = True
            # trade = pnl_long(buy_price)
            # while True:
            #     next_crypto_current = client.futures_ticker(symbol=symbol)['lastPrice']
            #     if trade == 'Profit':
            #         print('Position Closed')
            #         break
            #     if next_crypto_current == data['sma'][i]:
            #         print('Position Closed with Loss')
            #         current_loss = next_crypto_current - buy_price
            #         insert_data(buy_price, next_crypto_current, current_loss, 0.0)
            #
            #         break

        elif data['close'][i] < data['sma'][i] and in_position:
            # Sell signal
            print(data['sma'][i])
            # sell_price = float(data['close'][i])
            # in_position = False
            # trade = pnl_short(sell_price)
            # while True:
            #     next_crypto_current = client.futures_ticker(symbol=symbol)['lastPrice']
            #
            #     if trade == 'Profit':
            #         print('Position Closed')
            #     if next_crypto_current == data['sma'][i]:
            #         print('Position Closed with Loss')
            #         current_loss = sell_price - next_crypto_current
            #         insert_data(sell_price, next_crypto_current, current_loss, 0.0)
            #         break

    data['buy_signal'] = data['timestamp'].isin(buy_signals).astype(int)
    data['sell_signal'] = data['timestamp'].isin(sell_signals).astype(int)


if __name__ == "__main__":
    symbol = 'ETHUSDT'
    interval = '15m'
    # while True:
    historical_data = get_historical_klines(symbol, interval)  # Replace with your historical data file
    backtest_strategy(historical_data)
