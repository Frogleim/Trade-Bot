import threading
from miya import miya_trade
import time

data = None
not_empty = False


def clean_log_file():
    with open('./logs/signal_log.log', 'w') as log_file:
        log_file.write('')


def read_alert():
    global data, not_empty
    with open('./logs/signal_log.log', 'r') as alert_file:
        lines = alert_file.readlines()
        print(lines)
        if lines:
            data = lines[0].strip().split(', ')  # Split the line into parts
            not_empty = True
        else:
            not_empty = False
    return not_empty, lines


def start_trade(cryptocurrency, price, action, position_size):
    if action == 'Buy':
        threading.Thread(target=miya_trade.trade, args=(cryptocurrency, 'long', price, position_size, )).start()
        # run_trade.trade(cryptocurrency, price, action, position_size)
        print("Trade started for:", cryptocurrency)  # Adding a print statement
    elif action == 'Sell':
        threading.Thread(target=miya_trade.trade, args=(cryptocurrency, 'short', price, position_size,)).start()
        print("Trade started for:", cryptocurrency)  # Adding a print statement


def continuously_check_signals():
    while True:
        empty, data = read_alert()
        if empty:
            for line in data:
                parts = line.split()
                if len(parts) >= 8:
                    cryptocurrency = parts[5]
                    price = float(parts[6])
                    action = parts[7]
                    position_size = int(parts[8])
                    print(
                        f"Received signal for {cryptocurrency} at price {price} with action {action} position size {parts[8]}")
                    start_trade(cryptocurrency, price, action, position_size)
                    clean_log_file()
                    time.sleep(2)
                else:
                    print("Invalid data format for line:", line)
        else:
            print("No signals found.")
        time.sleep(5)


if __name__ == '__main__':
    continuously_check_signals()
