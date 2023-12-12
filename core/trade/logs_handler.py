import os
import logging
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "Trade-Bot")
logging.basicConfig(filename=f'{files_dir}/logs/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
error_handler = logging.FileHandler(f'{files_dir}/logs/error_logs.log')
error_handler.setLevel(logging.ERROR)  # Set the desired log level for the file
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
error_console_handler = logging.StreamHandler(sys.stdout)
error_console_handler.setLevel(logging.ERROR)  # Set the desired log level for the console
error_console_handler.setFormatter(error_formatter)
error_logger.addHandler(error_console_handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


def write_log_file(message):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(base_dir, '../../logs')
    with open(f'{files_dir}/trade_logs.txt', 'w', encoding='utf-8') as file:
        file.write(str(message))


def read_logs_txt():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(base_dir, '../../logs')

    with open(f'{files_dir}/trade_logs.txt', 'r', encoding='utf-8') as file:
        join_text = [line for line in file]
        print(join_text)
    return join_text


if __name__ == '__main__':
    mes = 'hello'
    write_log_file(mes)
