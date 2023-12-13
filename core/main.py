from trade import profitable_exit_strategy
import time


def run():
    count = 0

    while True:
        profitable_exit_strategy.trade()
        time.sleep(35)
        count += 1
        if count == 3:
            time.sleep(30 * 60)
            count = 0


if __name__ == '__main__':
    run()
