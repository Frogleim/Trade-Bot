from datetime import datetime, timedelta

import websocket
import threading
import json
import psycopg2


class DataBase:
    def __init__(self):
        self.user = "postgres"
        self.password = "0000"
        self.host = "localhost"
        self.port = 5432
        self.database = "StreamSignal"

    def connect(self):
        return psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

    def insert_trades(self, timestamp, quantity, price, side):
        conn = self.connect()
        cursor = conn.cursor()
        if side:
            cursor.execute("INSERT INTO trade_buyers (timestamp, quantity, side, price) VALUES (%s, %s, %s, %s)",
                           (timestamp, quantity, side, price))
        else:
            cursor.execute("INSERT INTO trade_sellers (timestamp, quantity, side, price) VALUES (%s, %s, %s, %s)",
                           (timestamp, quantity, side, price))
        conn.commit()

    def calculate_aggression_buyers(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) AS total_quantity, COUNT(*) AS total_count FROM trade_buyers;")
        record = cursor.fetchone()
        print("Total Buyers Quantity:", record[0])
        print("Total Buyers Count:", record[1])

    def calculate_aggression_sellers(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) AS total_quantity, COUNT(*) AS total_count FROM trade_sellers;")
        record = cursor.fetchone()
        print("Total Sellers Quantity:", record[0])
        print("Total Sellers Count:", record[1])

    def delete_rows_by_time(self, table_name, timestamp_column, start_time, end_time):
        conn = self.connect()
        cursor = conn.cursor()
        delete_query = f"DELETE FROM {table_name} WHERE {timestamp_column} >= %s AND {timestamp_column} < %s;"
        cursor.execute(delete_query, (start_time, end_time))
        conn.commit()


class Streaming(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def on_message(self, ws, msg):
        data = json.loads(msg)
        # Process the incoming message
        self.process_message(data)

    def on_error(self, ws, e):
        print('Error', e)

    def on_close(self, ws):
        print('Closing')

    def process_message(self, data):
        # Initialize your DataBase instance
        db = DataBase()

        # Get the current time
        current_time = datetime.now()

        # Update rows every 15 minutes
        if current_time.minute % 15 == 0:
            start_time = current_time - timedelta(minutes=15)
            end_time = current_time

            # Delete rows within the last 15 minutes
            db.delete_rows_by_time('trade_buyers', 'timestamp', start_time, end_time)
            db.delete_rows_by_time('trade_sellers', 'timestamp', start_time, end_time)

        # Insert the current trade
        db.insert_trades(current_time, data['q'], data['p'], data['m'])

        # Calculate aggression
        db.calculate_aggression_buyers()
        db.calculate_aggression_sellers()


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
    # try:
    #     connection = psycopg2.connect(user="postgres",
    #                                   password="0000",
    #                                   host="localhost",
    #                                   port="5432",
    #                                   database="StreamSignal")
    #     threading.Thread(target=StreamingOrderBook, args=('wss://fstream.binance.com/ws/xrpusdt@bookTicker', connection, )).start()
    #
    #     print("Connected to PostgreSQL")
    # except (Exception, psycopg2.Error) as error:
    #     print("Error while connecting to PostgreSQL:", error)
    threading.Thread(target=Streaming, args=('wss://fstream.binance.com/ws/xrpusdt@aggTrade',)).start()
    # threading.Thread(target=StreamingDepthBook, args=('wss://fstream.binance.com/ws/xrpusdt@depth', )).start()
    # threading.Thread(target=ForcedOrders, args=('wss://fstream.binance.com/ws/xrpusdt@forceOrder', )).start()
