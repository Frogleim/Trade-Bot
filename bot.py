from coins_trade.miya import miya_trade
from colorama import init, Fore
from binance.client import Client
from db import DataBase
import time

init()

client = Client()


def start_trade():
    traded = False
    my_db = DataBase()
    symbol, quantity, checkpoints = my_db.get_trade_coins()
    signal_data = my_db.get_signal(symbol=symbol)
    print(Fore.GREEN + f'Starting trade for symbol {symbol}')
    print(signal_data)
    if signal_data is not None:
        signal = signal_data[2]
        entry_price = signal_data[3]
        indicator = signal_data[5]
        miya_trade.trade(
            symbol=symbol,
            signal=signal,
            entry_price=entry_price,
            position_size=quantity,
            indicator=indicator
        )
        traded = True
        return traded
    print(Fore.RED + "No trade signals at this moment")


if __name__ == '__main__':
    print(Fore.YELLOW + 'Starting trade bot...')
    while True:
        is_traded = start_trade()
        time.sleep(5)
