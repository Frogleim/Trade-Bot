from binance.client import Client
from . import tp_sl, config, logging_settings
import time
from datetime import datetime

client = Client(config.API_KEY, config.API_SECRET)


def trade(symbol, signal, entry_price, start_time=None):
    current_time = datetime.now()

    if signal == 'short':
        tp_sl.profit_checkpoint_list.clear()
        tp_sl.current_profit = 0.00
        tp_sl.current_checkpoint = 0.00
        print(f'tp_sl.profit_checkpoint_list: {tp_sl.profit_checkpoint_list} --- {tp_sl.current_profit}')
        while True:

            res = tp_sl.pnl_short(entry_price, current_time)
            if res == 'Profit':
                print(f'Closing Position with {res}')
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break

    if signal == 'long':

        tp_sl.profit_checkpoint_list.clear()
        tp_sl.current_profit = 0.00
        tp_sl.current_checkpoint = 0.00

        print(f'tp_sl.profit_checkpoint_list: {tp_sl.profit_checkpoint_list} --- {tp_sl.current_profit}')
        while True:
            res = tp_sl.pnl_long(entry_price, current_time)
            if res == 'Profit':
                print(f'Closing Position with {res}')
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break



# 091
