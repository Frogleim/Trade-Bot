from trade import profitable_exit_strategy
import time
from trade import build_model


def run():
    trades_count = 0
    while True:
        build_model.train_base_model()
        profitable_exit_strategy.trade()
        trades_count += 1
        time.sleep(30 * 60)
        if trades_count == 12:
            trades_count = 0
            time.sleep(24*3600)


if __name__ == '__main__':
    run()
