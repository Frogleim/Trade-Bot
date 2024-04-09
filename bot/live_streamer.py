import strategy
import trade
from binance.client import Client
import logging_settings
import time

symbol = 'MATICUSDT'

client = Client(api_key='<KEY>', api_secret='<KEY>')
trading_pair = 'MATICUSDT'


def start_trade():
    long_entry_price, short_entry_price = strategy.get_signal()
    while True:
        current_price = client.futures_ticker(symbol=trading_pair)['lastPrice']

        if float(current_price) >= long_entry_price and short_entry_price:
            trade.run_trade(cryptocurrency=symbol, price=current_price, action='long')
            logging_settings.actions_logger.info('Long entry price: %.2f' % long_entry_price)
            break

        elif float(current_price) <= long_entry_price and short_entry_price:
            trade.run_trade(cryptocurrency=symbol, price=current_price, action='short')
            logging_settings.actions_logger.info('Short entry price: %.2f' % short_entry_price)
            break
        elif long_entry_price < float(current_price) < short_entry_price:
            logging_settings.actions_logger.info('Hold..: %.2f' % short_entry_price)
            continue


def run():
    print('Bot started')
    while True:
        print('Trading pair: %s' % trading_pair)
        print("---------------------------------")
        print('Waiting for price action...')
        start_trade()
        time.sleep(60)


if __name__ == '__main__':
    run()
