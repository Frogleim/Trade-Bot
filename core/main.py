from trade import profitable_exit_strategy


def run():
    while True:
        profitable_exit_strategy.trade()


if __name__ == '__main__':
    run()
