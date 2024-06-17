from model_building.strategies import MACD, BB, Dual_Thrust
from db import DataBase
from coins_trade.miya import logging_settings
from binance.client import Client
import asyncio

my_db = DataBase()
API_KEY, API_SECRET = my_db.get_binance_keys()
client = Client(API_KEY, API_SECRET)
technical_tool = ['MACD', 'Bollinger Bands']

pause_event = asyncio.Event()


async def fetch_macd_signal():
    df = await MACD.fetch_ohlcv()
    signals = MACD.generate_signals(df)
    signal = signals['signals'].iloc[-1]
    return 'MACD', signal


async def fetch_bb_signal():
    result = await BB.main()
    return 'Bollinger Bands', result[0], result[1]


async def fetch_thrust():
    df = await Dual_Thrust.fetch_ohlcv()
    signal = Dual_Thrust.dual_thrust_strategy(df)
    last_signal = df['signal'].iloc[-1]
    last_signal_time = df.index[-1]
    return 'Dual Thrust', last_signal


async def generate_signal():
    logging_settings.system_log.warning('Starting Miya Beta 0.07')
    pause_event.set()  # Initially start signal monitoring

    while True:
        await pause_event.wait()  # Wait until the event is set (unpaused)

        try:
            my_db.clean_db(table_name='signals')

            # Run all indicator functions concurrently
            results = await asyncio.gather(
                fetch_macd_signal(),
                fetch_bb_signal(),
                fetch_thrust()
            )

            # Process results
            signals = {name: signal for name, signal, *rest in results}
            prices = {name: rest[0] for name, signal, *rest in results if rest}
            print(signals)
            logging_settings.system_log.info(f'Signals: {signals}')
            logging_settings.system_log.info(f'Prices: {prices}')

            # Example logic for combined signals
            buy_signals = [name for name, signal in signals.items() if signal == 'Buy']
            sell_signals = [name for name, signal in signals.items() if signal == 'Sell']

            if buy_signals:
                entry_price = prices.get('Bollinger Bands', None)  # Use BB price if available
                my_db.insert_signal(symbol='MATICUSDT', signal='Buy', entry_price=entry_price)
                logging_settings.system_log.info(f'Getting Buy signal. Indicators: {buy_signals}')
                pause_event.clear()  # Pause after detecting a buy signal

            if sell_signals:
                entry_price = prices.get('Bollinger Bands', None)  # Use BB price if available
                my_db.insert_signal(symbol='MATICUSDT', signal='Sell', entry_price=entry_price)
                logging_settings.system_log.info(f'Getting Sell signal. Indicators: {sell_signals}')
                pause_event.clear()  # Pause after detecting a sell signal

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
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(generate_signal()),
        loop.create_task(monitor_signals())
    ]
    loop.run_until_complete(asyncio.wait(tasks))
