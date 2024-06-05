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

    def insert_trades(self, symbol, entry_price, signal):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO signals (coin, signal, entry_price) VALUES (%s, %s, %s)",
                       (symbol, signal, entry_price))
        conn.commit()


if __name__ == '__main__':
    db = DataBase()
    db.insert_trades(symbol='MATICUSDT', entry_price='0.77', signal='Buy')
