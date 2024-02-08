import time
from xrp import xrp_trade
from atom import atom_trade
from matic import matic_trade
from ada import ada_trade

is_empty = False
data = []

def read_alert():
    global is_empty, data
    with open('./logs/actions.log', 'r') as alert_file:
        lines = alert_file.readlines()
        if lines:
            data = lines[0].strip().split(', ')  # Split the line into parts
            is_empty = True
        else:
            is_empty = False
    return is_empty, data

def execute_trade():
    not_empty, alert_data = read_alert()
    if not_empty:
        symbol = alert_data[0].split(':')[1].strip()  # Extract symbol
        entry_price = float(alert_data[1].split(':')[1].strip())  # Extract entry price
        signal = alert_data[2].split(':')[1].strip()  # Extract signal

        if symbol == 'XRPUSDT':
            result = xrp_trade.trade(signal=signal, entry_price=entry_price)
        elif symbol == 'ATOMUSDT':
            result = atom_trade.trade(signal=signal, entry_price=entry_price)
        elif symbol == 'MATICUSDT':
            result = matic_trade.trade(signal=signal, entry_price=entry_price)
        elif symbol == 'ADAUSDT':
            result = ada_trade.trade(signal=signal, entry_price=entry_price)
        else:
            result = None
        return result
    else:
        return 'No trade'

if __name__ == '__main__':
    while True:
        r = execute_trade()
        print(r)
        time.sleep(30)