import db
from model_building.strategies import SMA21
from coins_trade.miya import logging_settings
import time

symbol = 'MATICUSDT'
sma = SMA21.SMA21(symbol)
my_db = db.DataBase()


def signal_check():
    logging_settings.system_log.warning('Starting SMA21 signals testing')
    while True:
        latest_data = sma.get_df_15m()
        my_db.insert_test_signals(
            close=float(latest_data['close']),
            sma21=float(latest_data['SMA21']),
            up_trigger_zone=float(latest_data['up_trigger_zone']),
            down_trigger_zone=float(latest_data['down_trigger_zone']),
            buy_signal=str(latest_data['Buy_Signal']),
            sell_signal=str(latest_data['Sell_Signal']),
            state=str(latest_data['State'])

        )
        logging_settings.actions_logger.info('SMA21 signal testing inserted successfully')
        time.sleep(60)


if __name__ == '__main__':
    signal_check()