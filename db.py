import psycopg2


class DataBase:
    def __init__(self):
        self.user = "postgres"
        self.password = "admin"
        self.host = "localhost"
        self.port = 5432
        self.database = "miya"

    def connect(self):
        return psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

    def clean_db(self, table_name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()

    def insert_signal(self, symbol, entry_price, signal):
        conn = self.connect()
        cursor = conn.cursor()
        self.clean_db(table_name='signals')
        cursor.execute("INSERT INTO signals (coin, signal, entry_price) VALUES (%s, %s, %s)",
                       (symbol, signal, entry_price))
        conn.commit()

    def insert_binance_keys(self, api_key, api_secret):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO binance_keys (api_key, api_secret) VALUES (%s, %s)", (api_key, api_secret))
        conn.commit()

    def insert_trades_coins(self, symbol, quantity, checkpoints):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO trade_coins (symbol, quantity, checkpoints) VALUES (%s, %s, %s)", (symbol, quantity, checkpoints))
        conn.commit()

    def get_signal(self, symbol):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM signals WHERE coin='{symbol}'")
        rows = cursor.fetchall()
        print(len(rows))
        if len(rows) > 0:
            return rows[-1]
        else:
            return None

    def check_is_finished(self):
        while True:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM trades_alert ")
            rows = cursor.fetchall()
            print(len(rows))

            if len(rows) > 0:
                return True
            else:
                return False

    def get_binance_keys(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT api_key, api_secret FROM binance_keys")
        row = cursor.fetchone()

        cursor.close()
        conn.close()
        if row:
            api_key = row[0]
            api_secret = row[1]
            return api_key, api_secret
        return None

    def get_trade_coins(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trade_coins")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        symbol = row[1]
        quantity = row[2]
        checkpoints = row[3]
        return symbol, quantity, checkpoints


if __name__ == '__main__':
    symbol = 'MATICUSDT'
    db = DataBase()
    rows = db.get_signal(symbol=symbol)
    print(rows)
