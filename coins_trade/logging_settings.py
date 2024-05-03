import os
import logging

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"bot")
user_count = None
log_file_path = os.path.join(files_dir, 'logs', 'logs.log')
actions_log_file_path = os.path.join(files_dir, 'logs', 'signal_log.log')
error_logs_log_file_path = os.path.join(files_dir, 'logs', 'error_logs.log')
finish_trade_log_file_path = os.path.join(files_dir, 'logs', 'finish_trade_log.log')
system_trade_log_file_path = os.path.join(files_dir, 'logs', 'system_trade_log.log')
# Define a formatter for log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Configure the root logger to print to terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # You can set the level to DEBUG to print all messages
console_handler.setFormatter(formatter)
logging.root.addHandler(console_handler)

# Configure the file handler for 'logs.log'
logging.basicConfig(filename=log_file_path, level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the 'actions.log' logger
actions_logger = logging.getLogger('signal_log')
actions_logger.setLevel(logging.INFO)
actions_handler = logging.FileHandler(actions_log_file_path)
actions_handler.setFormatter(formatter)
actions_logger.addHandler(actions_handler)

# Configure the 'finish_trade_log.log' logger
finish_trade_log = logging.getLogger('finish_trade_log')
finish_trade_log.setLevel(logging.INFO)
finish_trade_handler = logging.FileHandler(finish_trade_log_file_path)
finish_trade_handler.setFormatter(formatter)
finish_trade_log.addHandler(finish_trade_handler)

# Configure the 'error_logs.log' logger
error_logs_logger = logging.getLogger('error_logs_log')
error_logs_logger.setLevel(logging.ERROR)
error_logs_handler = logging.FileHandler(error_logs_log_file_path)
error_logs_handler.setFormatter(formatter)
error_logs_logger.addHandler(error_logs_handler)

# Configure the 'system_trade_log.log' logger
system_logs_logger = logging.getLogger('system_trade_log')
system_logs_logger.setLevel(logging.INFO)
system_logs_handler = logging.FileHandler(system_trade_log_file_path)
system_logs_handler.setFormatter(formatter)
system_logs_logger.addHandler(system_logs_handler)
