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
        print(msg)





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
            signal = self.analyze_trend(volume)
            self.prices.append(price)
            self.volumes.append(volume)
            if signal != "No significant trend confirmation":
                self.insert_signal(price, volume, timestamp, signal)




    def analyze_trend(self, volume):
        if len(self.prices) < 2 or len(self.volumes) < 2:
            print('No signal')
            return "No significant trend confirmation"

        current_price = self.prices[-1]
        previous_price = self.prices[-2]
        current_volume = self.volumes[-1]
        previous_volume = self.volumes[-2]

        if current_price > previous_price and current_volume > previous_volume:
            print('Potential buy signal')
            if volume > current_volume - previous_volume:
                return "Buy signal: Rising prices with increasing volume"
        elif current_price > previous_price and current_volume < previous_volume:
            if volume < current_volume - previous_volume:
                print('Potential buy signal')
                return "Sell signal: Rising prices with decreasing volume"
        return 'No significant trend confirmation'

    def insert_signal(self, price, volume, timestamp, signal):
        try:
            cursor =  self.connect.cursor()
            cursor.execute("INSERT INTO order_book_data (price, volume, timestamp) VALUES (%s, %s, %s)", (price, volume, timestamp))
            self.connect.commit()
            cursor.execute("INSERT INTO trend_signals (timestamp, signal, volumes) VALUES (%s, %s, %s)", (timestamp, signal, volume))

            self.connect.commit()

            cursor.close()
        except (Exception, psycopg2.Error) as error:
            print("Error while inserting data to PostgreSQL:", error)




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
    threading.Thread(target=Streaming, args=('wss://fstream.binance.com/ws/xrpusdt@trade', )).start()