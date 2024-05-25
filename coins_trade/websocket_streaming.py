from datetime import datetime, timedelta
import websocket
import threading
import json
import db
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import time


def message_handler(message):
    print(message)


class Streaming(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error,
                         )
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def on_message(self, ws, msg):
        data = json.loads(msg)
        print(data)
        # self.process_message(data)

    def on_error(self, ws, e):
        print('Error', e)

    def on_close(self, ws):
        print('Closing')

    def process_message(self, data):
        database = db.DataBase()
        current_time = datetime.now()
        if current_time.minute % 15 == 0:
            start_time = current_time - timedelta(minutes=15)
            end_time = current_time
            database.delete_rows_by_time('trade_buyers', 'timestamp', start_time, end_time)
            database.delete_rows_by_time('trade_sellers', 'timestamp', start_time, end_time)

        database.insert_trades(current_time, data['q'], data['p'], data['m'])
        buy_qty, buy_count = database.calculate_aggression_buyers()
        qty, count = database.calculate_aggression_sellers()

        database.insert_buy_signal(buy_qty, buy_count)
        database.insert_sells_signal(qty, count)


class StreamingDepthBook(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')
        self.total_bids = 0
        self.total_asks = 0
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def message(self, msg):
        data = json.loads(msg)
        if 'b' in data and 'a' in data:
            bids = data['b']
            asks = data['a']
            # Calculate total bids quantity
            total_bids_quantity = sum(float(bid[1]) for bid in bids)
            # Calculate total asks quantity
            total_asks_quantity = sum(float(ask[1]) for ask in asks)
            # Compare total bids and asks
            if total_bids_quantity > total_asks_quantity:
                print("There's more buying pressure (bullish)")
            elif total_bids_quantity < total_asks_quantity:
                print("There's more selling pressure (bearish)")
            else:
                print("Bids and asks are balanced")


class ForcedOrders(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')
        self.forced_orders = []
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def message(self, msg):
        data = json.loads(msg)
        if data.get('e') == 'forceOrder':
            self.forced_orders.append(data)
            self.algorithmic_trading()

    def algorithmic_trading(self):
        # Your algorithmic trading logic here
        # Example: Adjust trading parameters based on forced liquidation events
        frequency = len(self.forced_orders)
        severity = sum(float(order['o']['q']) for order in self.forced_orders)

        print(f"Frequency of forced liquidations: {frequency}")
        print(f"Total severity of forced liquidations: {severity}")


if __name__ == '__main__':
    my_client = UMFuturesWebsocketClient(on_message=message_handler)

    # Subscribe to a single symbol stream
    data = my_client.agg_trade(symbol="bnbusdt")
    print(data)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
    threading.Thread(target=ForcedOrders, args=('wss://fstream.binance.com/ws/xrpusdt@!aggTrade',)).start()
