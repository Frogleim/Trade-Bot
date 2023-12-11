from trade import profitable_exit_strategy
import time


def run():
    while True:
        profitable_exit_strategy.trade()
        time.sleep(30 * 60)


if __name__ == '__main__':
    run()
