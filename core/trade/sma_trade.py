import pandas as pd
import pandas_ta as ta
from binance.client import Client
import time
from tp_sl import pnl_short, pnl_long

# Replace with your Binance API key and secret
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

client = Client(api_key, api_secret)
sma_up_side: float
sma_down_side: float

symbol = 'ETHUSDT'
interval = '15m'  # Use '15m' for 15-minute intervals
length = 20

while True:
    # Fetch historical klines data
    klines = client.futures_klines(symbol=symbol, interval=interval)

    # Extract close prices from klines
    close_prices = [float(kline[4]) for kline in klines]

    # Create a DataFrame
    df = pd.DataFrame({'close': close_prices})

    # Calculate 15-minute SMA using pandas_ta
    df['sma'] = ta.sma(df['close'], length=length)
    # Get the last values
    live_price = client.futures_ticker(symbol=symbol)['lastPrice']
    last_sma_value = df['sma'].iloc[-1]
    sma_up_side = last_sma_value + 2
    sma_down_side = last_sma_value - 2

    print(f'Price: {live_price} --- SMA: {last_sma_value}')

    # Check if live price touches SMA
    if sma_up_side <= live_price <= sma_up_side:
        print(f'Live price touches SMA: {live_price}')

        # Wait for live price direction change
        while True:
            current_live_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
            # Long
            if current_live_price >= sma_up_side + 1:
                print(f'Live price went down by 4 points from SMA. Sell!')
                # Implement your sell logic here
                res = pnl_short(current_live_price, last_sma_value)
                if res == 'Profit':
                    print('Closing Position with Profit')
                    break
                if res == 'Loss':
                    print('Closing Position with Loss')
                    break
            # Short
            elif current_live_price <= sma_down_side - 1:
                print(f'Live price went up by 4 points from SMA. Buy!')
                # Implement your buy logic here
                res = pnl_long(current_live_price, last_sma_value)
                if res == 'Profit':
                    print('Closing Position with Profit')
                    break
                if res == 'Loss':
                    print('Closing Position with Loss')
                    break

            time.sleep(1)  # Adjust the sleep time as needed
