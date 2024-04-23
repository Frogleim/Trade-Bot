import time
from binance.client import Client
from . import tp_sl, config, position_handler, logging_settings
from datetime import datetime

client = Client(config.API_KEY, config.API_SECRET)


def trade(symbol, signal, entry_price, position_size):
    current_time = datetime.now()
    start_time = time.time()
    if signal == 'short':
        tp_sl.profit_checkpoint_list.clear()
        tp_sl.current_profit = 0.00
        tp_sl.current_checkpoint = 0.00

        try:
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=position_size,
                                                           symbol=symbol)
        except Exception as e:
            logging_settings.error_logs_logger.error(e)
            order_info = position_handler.place_sell_order(price=entry_price,
                                                           quantity=position_size,
                                                           symbol=symbol)
        while True:
            open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            if open_orders['status'] == 'NEW':
                if time.time() - start_time > 180:
                    print(time.time() - start_time)
                    print(open_orders['status'])
                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_short(entry_price, current_time)
                if res == 'Profit':

                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='long', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break

                if res == 'Loss':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='long', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break

    if signal == 'long':
        tp_sl.profit_checkpoint_list.clear()
        tp_sl.current_profit = 0.00
        tp_sl.current_checkpoint = 0.00

        try:
            order_info = position_handler.place_buy_order(price=entry_price, quantity=position_size,
                                                          symbol=symbol)
        except Exception as e:
            logging_settings.error_logs_logger.error(e)
            order_info = position_handler.place_buy_order(price=entry_price, quantity=position_size,
                                                          symbol=symbol)
        while True:
            open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            if open_orders['status'] == 'NEW':
                if time.time() - start_time > 180:
                    print(time.time() - start_time)
                    print(open_orders['status'])

                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_long(entry_price, current_time)
                if res == 'Profit':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='short', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break

                if res == 'Loss':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='short', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    break


