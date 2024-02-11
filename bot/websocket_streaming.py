from datetime import datetime

import websocket
import threading
import json
import psycopg2

class Streaming(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')

        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def message(self, msg):
        print(json.loads(msg)['p'])





class StreamingOrderBook(websocket.WebSocketApp):
    def __init__(self, url, db_connection):
        super().__init__(url=url, on_open=self.on_open)
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')
        self.connect = db_connection
        self.prices = []
        self.volumes = []
        self.run_forever()

    def on_open(self, ws):
        print('Websocket was opened')

    def message(self, msg):
        data = json.loads(msg)
        symbol = data.get('s')
        if symbol == 'XRPUSDT':
            price = float(data.get('b'))
            volume = float(data.get('B'))
            timestamp = datetime.now()
            signal = self.analyze_trend()
            if signal != "No significant trend confirmation":
                self.insert_data(price, volume, timestamp, signal)



    def analyze_trend(self):
        if len(self.prices) < 2 or len(self.volumes) < 2:
            print('No signal')
            return "No significant trend confirmation"

        current_price = self.prices[-1]
        previous_price = self.prices[-2]
        current_volume = self.volumes[-1]
        previous_volume = self.volumes[-2]

        if current_price > previous_price and current_volume > previous_volume:

            return "Confirmed uptrend: Rising prices with increasing volume"
        elif current_price < previous_price and current_volume > previous_volume:
            return "Potential downtrend reversal: Falling prices with increasing volume"
        elif current_price > previous_price and current_volume < previous_volume:
            return "Potential uptrend reversal warning: Rising prices with decreasing volume"
        else:
            print('No significant trend confirmation')

    def insert_data(self, price, volume, timestamp, signal):
        try:
            cursor =  self.connect.cursor()
            cursor.execute("INSERT INTO order_book_data (price, volume, timestamp) VALUES (%s, %s, %s)", (price, volume, timestamp))
            self.connect.commit()
            cursor.execute("INSERT INTO trend_signals (timestamp, signal) VALUES (%s, %s)", (timestamp, signal))
            self.connect.commit()

            cursor.close()
        except (Exception, psycopg2.Error) as error:
            print("Error while inserting data to PostgreSQL:", error)


if __name__ == '__main__':
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="0000",
                                      host="localhost",
                                      port="5432",
                                      database="StreamSignal")
        threading.Thread(target=StreamingOrderBook, args=('wss://fstream.binance.com/ws/xrpusdt@bookTicker', connection, )).start()

        print("Connected to PostgreSQL")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)