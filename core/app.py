import time

from core.trade import build_model


def start_train():
    while True:
        build_model.train_base_model()
        time.sleep(3000*60)


if __name__ == "__main__":
    start_train()