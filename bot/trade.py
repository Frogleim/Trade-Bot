import time
from xrp import xrp_trade
from atom import atom_trade
from matic import matic_trade
from ada import ada_trade
import logging_settings
import threading




def clean_log_file():
    with open('./logs/actions.log', 'w') as log_file:
        log_file.write('')
def read_alert():
    with open('./logs/actions.log', 'r') as alert_file:
        lines = alert_file.readlines()
        if lines:
            data = lines[0].strip().split(', ')  # Split the line into parts
            is_empty = True
        else:
            is_empty = False
    return is_empty, data

def run_trade(cryptocurrency, price, action):
    if cryptocurrency == 'XRPUSDT':
        start_time = time.time()
        clean_log_file()
        print('Clean alert file')
        print(f'Starting trade for symbol {cryptocurrency}')
        threading.Thread(target=xrp_trade.trade, args=(price, action, start_time)).start()
    elif cryptocurrency == 'ATOMUSDT':
        clean_log_file()
        print('Clean alert file')
        print(f'Starting trade for symbol {cryptocurrency}')
        threading.Thread(target=atom_trade.trade, args=(price, action)).start()
    elif cryptocurrency == 'MATICUSDT':
        clean_log_file()
        print('Clean alert file')
        print(f'Starting trade for symbol {cryptocurrency}')
        threading.Thread(target=matic_trade.trade, args=(price, action)).start()
    elif cryptocurrency == 'ADAUSDT':
        clean_log_file()
        print('Clean alert file')
        print(f'Starting trade for symbol {cryptocurrency}')
        threading.Thread(target=ada_trade.trade, args=(price, action)).start()
    else:
        print(f"Unknown cryptocurrency: {cryptocurrency}")



def continuously_check_signals():
    while True:
        is_empty, data = read_alert()
        if is_empty:
            cryptocurrency = data[0]
            price = float(data[1])
            action = data[2]
            print(f"Received signal for {cryptocurrency} at price {price} with action {action}")
            run_trade(cryptocurrency, price, action)
        else:
            print("No signals found.")
        time.sleep(5)

if __name__ == '__main__':
    continuously_check_signals()