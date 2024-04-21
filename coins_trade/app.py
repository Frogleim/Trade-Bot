import bot, trade
import threading


def main():
    print("Welcome to Coins Trade!")
    print("Running on Coins Trade")
    threading.Thread(target=bot.run).start()
    threading.Thread(target=trade.continuously_check_signals).start()
    print("Coins Trade is done!")


if __name__ == "__main__":
    main()