import strategy
import trade
from binance.client import Client
import logging_settings

symbol = 'MATICUSDT'

client = Client(api_key='<KEY>', api_secret='<KEY>')
trading_pair = 'MATICUSDT'


def start_trade():
    long_entry_price, short_entry_price = strategy.get_signal()
    while True:
        current_price = client.futures_ticker(symbol=trading_pair)['lastPrice']

        if float(current_price) - long_entry_price >= 0.002:
            trade.run_trade(cryptocurrency=symbol, price=long_entry_price, action='long')
            logging_settings.actions_logger.info('Long entry price: %.2f' % long_entry_price)

        elif float(current_price) - short_entry_price <= -0.002:
            trade.run_trade(cryptocurrency=symbol, price=short_entry_price, action='short')
            logging_settings.actions_logger.info('Short entry price: %.2f' % short_entry_price)
        else:
            logging_settings.actions_logger.info('Waiting for price action...')


def run():
    print('Bot started')
    while True:
        print('Trading pair: %s' % trading_pair)
        print("---------------------------------")
        print('Waiting for price action...')
        start_trade()


if __name__ == '__main__':
    run()