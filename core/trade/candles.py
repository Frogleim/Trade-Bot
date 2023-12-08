from binance.client import Client

# Binance API credentials
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

# Initialize the Binance client
client = Client(api_key, api_secret)


def is_last_candle_green(symbol, interval='3m'):
    # Retrieve the last candlestick data
    klines = client.get_klines(symbol=symbol, interval=interval, limit=2)

    if not klines:
        # Handle the case when no data is returned
        return None

    # Extract opening and closing prices from the last candlestick
    open_price = float(klines[0][1])  # Opening price
    close_price = float(klines[0][4])  # Closing price

    # Check if the last candlestick is green (closing price is higher than opening price)
    return close_price > open_price


# Example usage
symbol_to_check = 'ETHUSDT'
interval_to_check = '1m'

last_candle_is_green = is_last_candle_green(symbol_to_check, interval_to_check)

if last_candle_is_green is not None:
    if last_candle_is_green:
        print(f'The last candle is green (bullish). {last_candle_is_green}')
    else:
        print(f'The last candle is red (bearish). {last_candle_is_green}')
else:
    print('Unable to retrieve candlestick data.')
