import time
from binance.client import Client
from . import tp_sl, config, position_handler, logging_settings

# Replace with your Binance API key and secret
client = Client(config.API_KEY, config.API_SECRET)


def trade(symbol, signal, entry_price, start_time):
    if signal == 'Short':
        tp_sl.profit_checkpoint_list.clear()
        try:
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=config.position_size,
                                                           symbol=symbol)
        except Exception as e:
            print(e)
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=config.position_size,
                                                           symbol=symbol)
        while True:
            open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            if open_orders['status'] == 'NEW':
                if time.time() - start_time > 180:
                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_short(entry_price)
                if res == 'Profit':

                    print(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=config.position_size)
                    except Exception as e:
                        print(e)
                        position_handler.close_position(side='long', quantity=config.position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break
                elif time.time() - start_time > 10800:
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')

                    break

    if signal == 'Long':
        tp_sl.profit_checkpoint_list.clear()
        try:
            order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
                                                          symbol=symbol)
        except Exception as e:
            print(e)
            order_info = position_handler.place_buy_order(price=entry_price, quantity=config.position_size,
                                                          symbol=symbol)
        while True:
            open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            if open_orders['status'] == 'NEW':
                if time.time() - start_time > 180:
                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_long(entry_price)
                if res == 'Profit':
                    print(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=config.position_size)
                    except Exception as e:
                        print(e)
                        position_handler.close_position(side='short', quantity=config.position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break
                elif time.time() - start_time > 10800:
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')

                    break
