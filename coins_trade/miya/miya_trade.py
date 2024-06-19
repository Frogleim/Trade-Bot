import time
from binance.client import Client
from . import tp_sl, position_handler, logging_settings, db
from binance.exceptions import BinanceAPIException


my_db = db.DataBase()
API_KEY, API_SECRET = my_db.get_binance_keys()
client = Client(API_KEY, API_SECRET)


def trade(symbol, signal, entry_price, position_size, indicator):
    my_db.clean_db(table_name='signals')
    logging_settings.system_log.warning(f'Starting trade. Symbol: {symbol}, '
                                        f'Entry Price: {entry_price}, Position Size: {position_size}')
    if signal == 'Sell':
        start_time = time.time()
        print(f'Trade starting time: {start_time}')

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

            try:
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            except BinanceAPIException as be:
                logging_settings.error_logs_logger.error(be)
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))

            if open_orders['status'] == 'NEW':
                total_time = time.time() - start_time
                print(f'Total waiting time: {total_time}')
                if time.time() - start_time > 180:
                    client.futures_cancel_order(symbol=symbol, orderId=int(order_info['orderId']))
                    logging_settings.system_log.warning('Trade wasn\'t finished...too much time passed')
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    my_db.insert_trades_alerts()

                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                my_db.insert_trades_alerts()
                break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_short(entry_price, indicator)
                if res == 'Profit':

                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='long', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    my_db.insert_trades_alerts()

                    break

                if res == 'Loss':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='long', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='long', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    my_db.insert_trades_alerts()

                    break

    if signal == 'Buy':
        start_time = time.time()
        print(f'Trade starting time: {start_time}')

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

            try:
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))
            except BinanceAPIException as be:
                logging_settings.error_logs_logger.error(be)
                open_orders = client.futures_get_order(symbol=symbol, orderId=int(order_info['orderId']))

            if open_orders['status'] == 'NEW':
                total_time = time.time() - start_time

                print(f'Total waiting time: {total_time}')

                if time.time() - start_time > 180:
                    client.futures_cancel_order(symbol=symbol, orderId=int(order_info['orderId']))
                    logging_settings.system_log.warning('Trade wasn\'t finished...too much time passed')
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    my_db.insert_trades_alerts()

                    break
            if open_orders['status'] == 'CANCELED':
                logging_settings.finish_trade_log.info(f'{symbol} Finished')
                my_db.insert_trades_alerts()

                break
            if open_orders['status'] == 'FILLED':
                res = tp_sl.pnl_long(entry_price, indicator)
                if res == 'Profit':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='short', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    my_db.insert_trades_alerts()

                    break

                if res == 'Loss':
                    logging_settings.actions_logger.info(f'Closing Position with {res}')
                    try:
                        position_handler.close_position(side='short', quantity=position_size)
                    except Exception as e:
                        logging_settings.error_logs_logger.error(e)
                        position_handler.close_position(side='short', quantity=position_size)
                    logging_settings.finish_trade_log.info(f'{symbol} Finished')
                    my_db.insert_trades_alerts()

                    break


