import pandas as pd
from binance.client import Client
import pandas_ta as ta
import mplfinance as mpf
import matplotlib.pyplot as plt

# Replace 'your_api_key' and 'your_api_secret' with your actual Binance API key and secret
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

starting_capital = 13.0  # Starting capital in USDT
capital = starting_capital
position_size = 1.0  # Fixed position size for each trade
stop_loss_threshold = -10  # Stop-loss threshold in percentage
take_profit_threshold = 10  # Take-profit threshold in percentage

# Function to get historical data for a trading pair
def get_historical_data(symbol, interval, limit):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Convert string columns to numeric
    numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    df.set_index('timestamp', inplace=True)
    return df

# Function to apply the strategy to a sideways market
def sideways_market_strategy(data):
    # Calculate Bollinger Bands
    data['sma'] = data['close'].rolling(window=20).mean()
    data['upper_band'] = data['sma'] + 2 * data['close'].rolling(window=20).std()
    data['lower_band'] = data['sma'] - 2 * data['close'].rolling(window=20).std()

    # Identify key reversal points
    key_levels = data[data['close'].diff().shift(-1) * data['close'].diff() < 0]['close']

    # Check for band touch near key levels
    signals = []

    for level in key_levels:
        # Find the corresponding row in the data
        row = data[data['close'] == level].index[0]

        # Check if the price touched upper or lower band
        if data['close'][row] > data['upper_band'][row]:
            signals.append(('Short', row, data['close'][row]))

        elif data['close'][row] < data['lower_band'][row]:
            signals.append(('Long', row, data['close'][row]))

    return signals

# Backtesting function
def backtest(data, signals):
    global capital
    position = 0  # 0 for no position, 1 for long, -1 for short
    entry_price = 0  # Entry price for the current position

    for signal in signals:
        action, timestamp, price = signal

        if action == 'Long' and position != 1:
            # Enter long position
            position = 1
            entry_price = price
            capital -= price * position_size
            print(f"Entering Long Position at {timestamp} - Price: {price} - Remaining Capital: {capital}")

        elif action == 'Short' and position != -1:
            # Enter short position
            position = -1
            entry_price = price
            capital -= price * position_size
            print(f"Entering Short Position at {timestamp} - Price: {price} - Remaining Capital: {capital}")

        # Check for stop-loss and take-profit conditions
        if position == 1 and (price - entry_price) >= take_profit_threshold:
            # Take-profit condition for long position
            capital += price * position_size
            position = 0
            print(f"Closing Long Position at {timestamp} - Take-Profit - Price: {price} - Remaining Capital: {capital}")

        elif position == -1 and (entry_price - price) >= stop_loss_threshold:
            # Stop-loss condition for short position
            capital += price * position_size
            position = 0
            print(f"Closing Short Position at {timestamp} - Stop-Loss - Price: {price} - Remaining Capital: {capital}")

    # Close any open position at the end of the backtest
    if position != 0:
        capital += data['close'].iloc[-1] * position_size * position
        print(f"Closing Position at the end of backtest - Final Capital: {capital}")

    return capital

# Get historical data for ETHUSDT with 15-minute interval
symbol = 'ETHUSDT'
interval = '15m'
limit = 1000  # You can adjust this based on the amount of historical data you want
data = get_historical_data(symbol, interval, limit)

# Apply the strategy to the historical data
signals = sideways_market_strategy(data)

# Backtest the strategy
final_capital = backtest(data, signals)
print(f"Initial Capital: {starting_capital} - Final Capital: {final_capital}")

# Visualize the data with Bollinger Bands
apds = [mpf.make_addplot(data['sma'], color='blue'),
        mpf.make_addplot(data['upper_band'], color='orange'),
        mpf.make_addplot(data['lower_band'], color='orange')]

# Plot entry signals
fig, axlist = mpf.plot(data, type='candle', addplot=apds, show_nontrading=True, warn_too_much_data=len(data), returnfig=True)
cursor = mpf.make_addplot(data['close'], scatter=True, markersize=0, color='blue', panel=1, secondary_y=False)

# Add scatter plots for entry signals
for signal in signals:
    action, timestamp, price = signal
    marker = '^' if action == 'Long' else 'v'
    color = 'green' if action == 'Long' else 'red'
    axlist[0].scatter(timestamp, price, marker=marker, color=color, label=f'{action} Entry Signal')

# Show the plot
mpf.show()
