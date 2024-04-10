from binance.client import Client
from . import tp_sl, config, logging_settings
import time

client = Client(config.API_KEY, config.API_SECRET)


def trade(symbol, signal, entry_price, start_time):
    if signal == 'short':
        tp_sl.profit_checkpoint_list.clear()
        while True:

            res = tp_sl.pnl_short(entry_price)
            if res == 'Profit':
                print(f'Closing Position with {res}')
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break

    if signal == 'long':
        tp_sl.profit_checkpoint_list.clear()
        while True:
            res = tp_sl.pnl_long(entry_price)
            if res == 'Profit':
                print(f'Closing Position with {res}')
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break



# 091
