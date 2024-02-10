import websocket
import threading
import json


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


threading.Thread(target=Streaming, args=('wss://fstream.binance.com/ws/btcusdt@markPrice', )).start()