import psycopg2


class DataBase:
    def __init__(self):
        self.user = "postgres"
        self.password = "admin"
        self.host = "localhost"
        self.port = 5432
        self.database = "TradeBot"

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

    def insert_test_trades(self, entry_time, entry_price, close_price, pnl, side, exit_time):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_trades (entry_time, entry_price, exit_price, pnl, side, exit_price)"
                       "VALUES (%s, %s, %s, %s, %s, %s)",
                       (entry_time, entry_price, close_price, pnl, side, exit_time))
        conn.commit()

