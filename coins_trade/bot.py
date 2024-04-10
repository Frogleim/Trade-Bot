import strategy
import trade
from binance.client import Client
import logging_settings
import time

symbol = 'MATICUSDT'

client = Client(api_key='<KEY>', api_secret='<KEY>')
trading_pair = 'MATICUSDT'


def start_trade():
    signal, price = strategy.main()
    current_price = client.futures_ticker(symbol=trading_pair)['lastPrice']
    if signal == "Buy":
        trade.run_trade(cryptocurrency=symbol, price=current_price, action='long')
        logging_settings.actions_logger.info('Long entry price: %.2f' % price)

    elif signal == "Sell":
        trade.run_trade(cryptocurrency=symbol, price=current_price, action='short')
        logging_settings.actions_logger.info('Short entry price: %.2f' % price)


def run():
    print('Bot started')
    print('Waiting for 30 min before starting... ')
    while True:
        time.sleep(1800)

        print('Trading pair: %s' % trading_pair)
        print("---------------------------------")
        print('Waiting for price action...')
        start_trade()


if __name__ == '__main__':
    run()
