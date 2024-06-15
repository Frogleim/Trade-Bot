from model_building.strategies import patterns, BB, MACD
from db import DataBase
from coins_trade.miya import logging_settings
from binance.client import Client
import asyncio

my_db = DataBase()
API_KEY, API_SECRET = my_db.get_binance_keys()
client = Client(API_KEY, API_SECRET)
technical_tool = ['MACD', 'Bollinger Bands']


async def fetch_macd_signal():
    df = await MACD.fetch_ohlcv()
    signals = MACD.generate_signals(df)
    signal = signals['signals'].iloc[-1]
    return 'MACD', signal


async def fetch_bb_signal():
    signal, price = await BB.check_sma()
    return 'Bollinger Bands', signal, price


async def generate_signal():
    logging_settings.system_log.info('Starting Miya Beta 0.02')
    while True:
        try:
            my_db.clean_db(table_name='signals')

            # Run all indicator functions concurrently
            results = await asyncio.gather(
                # fetch_macd_signal(),
                fetch_bb_signal(),
            )

            # Process results
            signals = {name: signal for name, signal, *rest in results}
            prices = {name: rest[0] for name, signal, *rest in results if rest}

            logging_settings.system_log.info(f'Signals: {signals}')
            logging_settings.system_log.info(f'Prices: {prices}')

            # Example logic for combined signals
            buy_signals = [name for name, signal in signals.items() if signal == 'Buy']
            sell_signals = [name for name, signal in signals.items() if signal == 'Sell']

            if buy_signals:
                entry_price = prices.get('Bollinger Bands', None)  # Use BB price if available
                my_db.insert_signal(symbol='MATICUSDT', signal='Buy', entry_price=entry_price)
                logging_settings.system_log.info(f'Getting Buy signal. Indicators: {buy_signals}')
                my_db.check_is_finished()
                my_db.clean_db(table_name='signals')
                my_db.clean_db(table_name='trades_alert')

            if sell_signals:
                entry_price = prices.get('Bollinger Bands', None)  # Use BB price if available
                my_db.insert_signal(symbol='MATICUSDT', signal='Sell', entry_price=entry_price)
                logging_settings.system_log.info(f'Getting Sell signal. Indicators: {sell_signals}')
                my_db.check_is_finished()
                my_db.clean_db(table_name='signals')
                my_db.clean_db(table_name='trades_alert')

        except Exception as e:
            logging_settings.error_logs_logger.error(f'Error in generate_signal: {e}')

        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(generate_signal())
