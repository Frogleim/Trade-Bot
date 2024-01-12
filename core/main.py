from core.trade.ETH import sma_eth


def run():
    print('Starting to trade')
    sma_eth.trade()


if __name__ == '__main__':
    while True:
        run()