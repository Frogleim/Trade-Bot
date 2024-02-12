import backtrader as bt
import pandas as pd
from binance.client import Client


class YourDataFeedClass(bt.feeds.PandasData):
    params = (
        ('datetime', 0),  # Index of the timestamp column
        ('open', 1),  # Index of the open price column
        ('high', 2),  # Index of the high price column
        ('low', 3),  # Index of the low price column
        ('close', 4),  # Index of the close price column
        ('volume', 5),  # Index of the volume column
        ('openinterest', -1),  # Index of the open interest column (-1 if not available)
    )

    # Fetch historical candlestick data from Binance Futures API
    def __init__(self, symbol, timeframe, api_key, api_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client = Client(api_key, api_secret)
        candles = client.futures_klines(symbol=symbol, interval=timeframe)
        df = pd.DataFrame(candles)
        df['timestamp'] = pd.to_datetime(df[0], unit='ms')
        df.set_index('timestamp', inplace=True)
        self.df = df

    def start(self):
        super().start()
        self.df_iter = self.df.iterrows()

    def _load(self):
        try:
            idx, row = next(self.df_iter)
        except StopIteration:
            return False
        self.lines.datetime[0] = bt.date2num(idx)
        self.lines.open[0] = float(row[1])
        self.lines.high[0] = float(row[2])
        self.lines.low[0] = float(row[3])
        self.lines.close[0] = float(row[4])
        self.lines.volume[0] = float(row[5])
        return True


class TrendVolumeStrategy(bt.Strategy):
    def __init__(self):
        self.trend_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
        self.volume = self.data.volume

    def next(self):
        if self.position:  # Check if already in a trade
            if self.data.close < self.trend_ma and self.volume > self.volume[-1]:
                self.sell()  # Close the existing long position
            elif self.data.close > self.trend_ma and self.volume < self.volume[-1]:
                self.buy()  # Close the existing short position
        else:
            if self.data.close > self.trend_ma and self.volume > self.volume[-1]:
                self.buy()  # Open a long position
            elif self.data.close < self.trend_ma and self.volume < self.volume[-1]:
                self.sell()  # Open a short position


# Create a cerebro instance
cerebro = bt.Cerebro()

# Add the data feed
symbol = 'XRPUSDT'  # Symbol for XRP/USDT perpetual contract
timeframe = Client.KLINE_INTERVAL_1DAY  # 1-day candlesticks
api_key = 'your_api_key'  # Replace with your actual API key
api_secret = 'your_api_secret'  # Replace with your actual API secret
data = YourDataFeedClass(symbol=symbol, timeframe=timeframe, api_key=api_key, api_secret=api_secret)
cerebro.adddata(data)

# Add the strategy
cerebro.addstrategy(TrendVolumeStrategy)

# Set starting capital
starting_capital = 10000
cerebro.broker.setcash(starting_capital)

# Set commission and slippage
cerebro.broker.setcommission(commission=0.001)  # Replace with your specific commission value
cerebro.broker.set_slippage_fixed(slippage=0.001)  # Replace with your specific slippage value

# Set position sizing (if required)
cerebro.addsizer(bt.sizers.FixedSize, stake=1)

# Run the backtest
cerebro.run()

# Print final portfolio value
print(f"Final Portfolio Value: {cerebro.broker.getvalue()}")

# Plot the results (optional, requires matplotlib)
cerebro.plot()
