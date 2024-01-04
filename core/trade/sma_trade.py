import pandas as pd
import pandas_ta as ta
from binance.client import Client
from . import position_handler, config, files_manager, tp_sl
import time
# from tp_sl import pnl_short, pnl_long

# Replace with your Binance API key and secret
api_key = 'iyJXPaZztWrimkH6V57RGvStFgYQWRaaMdaYBQHHIEv0mMY1huCmrzTbXkaBjLFh'
api_secret = 'hmrus7zI9PW2EXqsDVovoS2cEFRVsxeETGgBf4XJInOLFcmIXKNL23alGRNRbXKI'

client = Client(api_key, api_secret)

symbol = 'ETHUSDT'
interval = '15m'  # Use '15m' for 15-minute intervals
length = 20

closed = False
def calculate_sma(symbol, interval, length):
    klines = client.futures_klines(symbol=symbol, interval=interval)
    close_prices = [float(kline[4]) for kline in klines]
    df = pd.DataFrame({'close': close_prices})
    df['sma'] = ta.sma(df['close'], length=length)
    return df['sma'].iloc[-1]


def check_sma():
    while True:
        sma_value = calculate_sma(symbol, interval, length)
        sma_up_side = sma_value + 1
        sma_down_side = sma_value - 1
        live_price = float(client.futures_ticker(symbol=symbol)['lastPrice'])
        print(f'Price: {live_price} --- SMA: {sma_value}')
        if sma_down_side <= live_price <= sma_up_side:
            print(f'Live price touches SMA: {live_price}')
            return True, sma_up_side, sma_down_side, sma_value
        else:
            continue

def break_point():
    is_open, sma_up, sma_down, sma = check_sma()

    while True:
        current_live_price = float(client.futures_ticker(symbol=symbol)['lastPrice'])
        print(f'Checking entry position')
        if current_live_price <= sma_down - 3:
            print(f'Live price went down by 2 points from SMA. Sell!')
            return 'Sell', current_live_price, sma
        elif current_live_price >= sma_up + 3:
            print(f'Live price went up by 2 points from SMA. Buy!')
            return 'Buy', current_live_price, sma
        else:
            continue



def trade():
    global closed
    signal, entry_price, sma = break_point()
    if signal == 'Buy':

        tp_sl.profit_checkpoint_list.clear()
        # try:
        #     order_info = position_handler.place_sell_order(price=entry_price,
        #                                                   quantity=config.position_size,
        #                                                   symbol=config.trading_pair)
        # except Exception as e:
        #     print(e)
        #     order_info = position_handler.place_sell_order(price=entry_price,
        #                                                   quantity=config.position_size,
        #                                                    symbol=config.trading_pair)
        # # Implement your sell logic here
        while True:
            # ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            # open_orders = client.futures_get_order(symbol=config.trading_pair,
            #                                        orderId=int(order_info['orderId']))
            # if open_orders['status'] == 'NEW':
            #     if float(ticker) - float(open_orders['price']) > 3:
            #         client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
            #         break
            # if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_long(entry_price, sma)
                if res == 'Profit' or res == 'Loss':
                    print(f'Closing Position with {res}')
                    # try:
                    #     position_handler.close_position(side='long', quantity=config.position_size)
                    # except Exception as e:
                    #     print(e)
                    #     position_handler.close_position(side='long', quantity=config.position_size)
                    break
    if signal == 'Sell':
        # Cleaning checkpoint list before trade
        tp_sl.profit_checkpoint_list.clear()


        # try:
        #     order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
        #                                                symbol=config.trading_pair)
        # except Exception as e:
        #     print(e)
        #     order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
        #                                                   symbol=config.trading_pair)

        # Implement your buy logic here
        while True:
            # ticker = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
            # open_orders = client.futures_get_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
            # if open_orders['status'] == 'NEW':
            #     if float(ticker) - float(open_orders['price']) > 3:
            #         client.futures_cancel_order(symbol=config.trading_pair, orderId=int(order_info['orderId']))
            #         break
            # if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_short(entry_price, sma)
                if res == 'Profit' or res == 'Loss':
                    print(f'Closing Position with {res}')
                    # try:
                    #     position_handler.close_position(side='short', quantity=config.position_size)
                    # except Exception as e:
                    #     print(e)
                    #     position_handler.close_position(side='short', quantity=config.position_size)
                    break





if __name__ == '__main__':
    while True:
        trade()
