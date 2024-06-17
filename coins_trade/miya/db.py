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

    def insert_trades(self, symbol, entry_price, close_price, pnl, side, time_in_trade):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trades (symbol, entry_price, close_price, pnl, side) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (symbol, entry_price, close_price, pnl, side))
        conn.commit()

    def insert_test_trades(self, symbol, entry_price, close_price, pnl, indicator):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trades_history (symbol, entry_price, exit_price, profit, indicator)"
                       "VALUES (%s, %s, %s, %s, %s)",
                       (symbol, entry_price, close_price, pnl, indicator))
        self.insert_trades_alerts()
        conn.commit()

    def insert_trades_alerts(self):
        conn = self.connect()
        cursor = conn.cursor()
        is_finished = "True"
        cursor.execute("INSERT INTO trade_alerts (is_finished) VALUES (%s)"
                       ,
                       is_finished)
        conn.commit()

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
    my_db = DataBase()
    my_db.get_trade_coins()
