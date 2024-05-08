import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta

# Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
symbol = 'MATICUSDT'
initial_wallet = 200.0
investment_percent = 0.05
ma_period = 50  # Moving average period
timeframe = Client.KLINE_INTERVAL_1HOUR  # 1-hour interval

# Fetch historical data
today = datetime.now()
one_year_ago = today - timedelta(days=365)
klines = client.futures_historical_klines(symbol, timeframe, one_year_ago.strftime("%d %b, %Y"), today.strftime("%d %b, %Y"))

# Prepare data
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data['close'] = pd.to_numeric(data['close'])
data['date'] = data['timestamp'].dt.date

# Calculate moving average
data['ma'] = data['close'].rolling(window=ma_period).mean()

# Simulation
wallet = initial_wallet
positions = 0
entry_price = 0
last_date = None
trade_count = 0

for index, row in data.iterrows():
    if last_date != row['date']:
        trade_count = 0  # Reset trade count each new day
        last_date = row['date']

    if trade_count < 10 and row['ma'] is not None:  # Limit trades to 10 per day
        if row['close'] > row['ma'] and positions == 0:
            # Buy
            entry_price = row['close']
            invest_amount = wallet * investment_percent
            positions = invest_amount / entry_price
            wallet -= invest_amount  # Deduct investment from wallet
            trade_count += 1
            print(f"{row['timestamp']} - Buying at {entry_price}, positions: {positions}, wallet: {wallet}")
        elif positions > 0:
            take_profit_price = entry_price + 0.0060
            stop_loss_price = entry_price - 0.0045
            # Check for sell conditions
            if row['close'] >= take_profit_price:
                # Take profit
                wallet += positions * take_profit_price
                print(f"{row['timestamp']} - Taking profit at {take_profit_price}, wallet: {wallet}")
                positions = 0
                trade_count += 1
            elif row['close'] <= stop_loss_price:
                # Stop loss
                wallet += positions * stop_loss_price
                print(f"{row['timestamp']} - Stopping loss at {stop_loss_price}, wallet: {wallet}")
                positions = 0
                trade_count += 1

print(f"Final wallet balance: {wallet}")
