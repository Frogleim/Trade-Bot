from core.strategies import MACD, BB, Dual_Thrust, SMA21, EMA_Cross
from db import DataBase
from coins_trade.miya import logging_settings
from binance.client import Client
import bot
import asyncio

my_db = DataBase()
try:
    API_KEY, API_SECRET = my_db.get_binance_keys()
    client = Client(API_KEY, API_SECRET)
except Exception as e:
    custom_message = "Error occurred while fetching Binance keys and initializing the client."
    logging_settings.error_logs_logger.error(f"{custom_message}: {e}")
    raise Exception(custom_message)

pause_event = asyncio.Event()

async def fetch_ema_cross():
    symbol, signal, close_price = await EMA_Cross.check_signal()
    return 'EMA', signal, symbol, close_price

async def generate_signal():
    logging_settings.system_log.warning('Starting Miya Beta 0.1.9')
    pause_event.set()

    while True:
        await pause_event.wait()

        try:
            my_db.clean_db(table_name='signals')
            my_db.clean_db(table_name='trades_alert')

            # Run all indicator functions concurrently
            results = await asyncio.gather(
                fetch_ema_cross()
            )

            # Process results
            signals = {name: (signal, rest[0]) for name, signal, *rest in results if rest}
            prices = {name: rest[1] for name, signal, *rest in results if len(rest) > 1}

            print(signals)
            logging_settings.system_log.info(f'Signals: {signals}')
            logging_settings.system_log.info(f'Prices: {prices}')

            # Example logic for combined signals
            buy_signals = [(name, symbol) for name, (signal, symbol) in signals.items() if signal == 'Buy']
            sell_signals = [(name, symbol) for name, (signal, symbol) in signals.items() if signal == 'Sell']

            if buy_signals:
                symbol = buy_signals[0][1]
                entry_price = client.futures_ticker(symbol=symbol)['lastPrice']

                my_db.insert_signal(
                    symbol=symbol,
                    signal='Buy',
                    entry_price=entry_price,
                    indicator=buy_signals[0][0]
                )
                logging_settings.actions_logger.info(f'Getting Buy signal for {symbol}. Indicators: {[s[0] for s in buy_signals]}')
                pause_event.clear()  # Pause after detecting a buy signal
                await bot.start_trade()
                # await asyncio.sleep(60)

            if sell_signals:
                symbol = sell_signals[0][1]
                entry_price = client.futures_ticker(symbol=symbol)['lastPrice']

                my_db.insert_signal(
                    symbol=symbol,
                    signal='Sell',
                    entry_price=entry_price,
                    indicator=sell_signals[0][0]
                )
                logging_settings.actions_logger.info(f'Getting Sell signal for {symbol}. Indicators: {[s[0] for s in sell_signals]}')
                pause_event.clear()  # Pause after detecting a sell signal
                # await asyncio.sleep(60)
                await bot.start_trade()

        except Exception as e:
            logging_settings.error_logs_logger.error(f'Error in generate_signal: {e}')

        await asyncio.sleep(5)

async def monitor_signals():
    while True:
        await asyncio.sleep(1)  # Check every second
        is_finished = my_db.check_is_finished()
        if is_finished:
            my_db.clean_db(table_name='signals')
            my_db.clean_db(table_name='trades_alert')
            pause_event.set()  # Resume signal monitoring

if __name__ == '__main__':
    my_db.create_all_tables()
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(generate_signal()),
        loop.create_task(monitor_signals()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
