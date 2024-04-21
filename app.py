from coins_trade import bot, trade


def main():
    print("Welcome to Coins Trade!")
    print("Running on Coins Trade")
    bot.run()
    trade.continuously_check_signals()
    print("Coins Trade is done!")


if __name__ == "__main__":
    main()