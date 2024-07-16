import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tabulate import tabulate
import warnings

warnings.filterwarnings('ignore')
from binance.client import Client


def MovingAverageCrossStrategyBinance(stock_symbol='MATICUSDT', interval='15m', lookback_period='1 month',
                                      short_window=8, long_window=25, moving_avg='SMA', display_table=True):
    '''
    The function takes the stock symbol, interval, look-back period,
    look-back windows for moving averages, and the moving-average type(SMA or EMA) as input
    and returns the respective MA Crossover chart along with the buy/sell signals for the given period.
    '''
    # Initialize Binance client
    api_key = 'YOUR_BINANCE_API_KEY'
    api_secret = 'YOUR_BINANCE_API_SECRET'
    client = Client(api_key, api_secret)

    # Calculate the start date based on the lookback period
    end_date = datetime.now()
    if lookback_period.endswith('month'):
        months = int(lookback_period.split()[0])
        start_date = end_date - timedelta(days=30 * months)
    else:
        raise ValueError("Invalid lookback period format. Use 'X month' where X is the number of months.")

    start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

    # Fetch historical klines for the specified symbol and interval
    klines = client.futures_historical_klines(stock_symbol, interval, start_str, end_str)

    # Convert the fetched data to a DataFrame
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
               'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    stock_df = pd.DataFrame(klines, columns=columns)

    # Convert the timestamp to datetime
    stock_df['timestamp'] = pd.to_datetime(stock_df['timestamp'], unit='ms')
    stock_df.set_index('timestamp', inplace=True)

    # Select only the 'close' column and convert to float
    stock_df['Close Price'] = stock_df['close'].astype(float)

    # Drop unnecessary columns
    stock_df = stock_df[['Close Price']]

    # column names for long and short moving average columns
    short_window_col = str(short_window) + '_' + moving_avg
    long_window_col = str(long_window) + '_' + moving_avg

    if moving_avg == 'SMA':
        # Create a short simple moving average column
        stock_df[short_window_col] = stock_df['Close Price'].rolling(window=short_window, min_periods=1).mean()

        # Create a long simple moving average column
        stock_df[long_window_col] = stock_df['Close Price'].rolling(window=long_window, min_periods=1).mean()

    elif moving_avg == 'EMA':
        # Create short exponential moving average column
        stock_df[short_window_col] = stock_df['Close Price'].ewm(span=short_window, adjust=False).mean()

        # Create a long exponential moving average column
        stock_df[long_window_col] = stock_df['Close Price'].ewm(span=long_window, adjust=False).mean()

    # create a new column 'Signal' such that if faster moving average is greater than slower moving average
    # then set Signal as 1 else 0.
    stock_df['Signal'] = 0.0
    stock_df['Signal'] = np.where(stock_df[short_window_col] > stock_df[long_window_col], 1.0, 0.0)

    # create a new column 'Position' which is a day-to-day difference of the 'Signal' column.
    stock_df['Position'] = stock_df['Signal'].diff()

    # plot close price, short-term and long-term moving averages
    plt.figure(figsize=(20, 10))
    plt.tick_params(axis='both', labelsize=14)
    stock_df['Close Price'].plot(color='k', lw=1, label='Close Price')
    stock_df[short_window_col].plot(color='b', lw=1, label=short_window_col)
    stock_df[long_window_col].plot(color='g', lw=1, label=long_window_col)

    # plot 'buy' signals
    plt.plot(stock_df[stock_df['Position'] == 1].index,
             stock_df[short_window_col][stock_df['Position'] == 1],
             '^', markersize=15, color='g', alpha=0.7, label='buy')

    # plot 'sell' signals
    plt.plot(stock_df[stock_df['Position'] == -1].index,
             stock_df[short_window_col][stock_df['Position'] == -1],
             'v', markersize=15, color='r', alpha=0.7, label='sell')
    plt.ylabel('Price in $', fontsize=16)
    plt.xlabel('Date', fontsize=16)
    plt.title(str(stock_symbol) + ' - ' + str(moving_avg) + ' Crossover', fontsize=20)
    plt.legend()
    plt.grid()
    plt.show()

    if display_table == True:
        df_pos = stock_df[(stock_df['Position'] == 1) | (stock_df['Position'] == -1)]
        df_pos['Position'] = df_pos['Position'].apply(lambda x: 'Buy' if x == 1 else 'Sell')
        print(tabulate(df_pos, headers='keys', tablefmt='psql'))


# Example usage
MovingAverageCrossStrategyBinance(stock_symbol='MATICUSDT', interval='15m', lookback_period='1 month',
                                  short_window=8, long_window=25, moving_avg='SMA', display_table=True)
