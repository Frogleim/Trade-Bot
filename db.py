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

    def clean_db(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM signals")
        conn.commit()

    def insert_trades(self, symbol, entry_price, signal):
        conn = self.connect()
        cursor = conn.cursor()
        self.clean_db()
        cursor.execute("INSERT INTO signals (coin, signal, entry_price) VALUES (%s, %s, %s)",
                       (symbol, signal, entry_price))
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


if __name__ == '__main__':
    symbol = 'MATICUSDT'
    db = DataBase()
    rows = db.get_signal(symbol=symbol)
    print(rows)
