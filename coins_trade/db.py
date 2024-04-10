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

    def insert_trades(self, symbol, entry_price, close_price, pnl):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trades (symbol, entry_price, close_price, pnl, side) VALUES (%s, %s, %s, %s)",
                       (symbol, entry_price, close_price, pnl))
        conn.commit()

    def calculate_aggression_buyers(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) AS total_quantity, COUNT(*) AS total_count FROM trade_buyers;")
        record = cursor.fetchone()
        print("Total Buyers Quantity:", record[0])
        print("Total Buyers Count:", record[1])
        total_quantity = record[0]
        total_count = record[1]
        return total_quantity, total_count

    def calculate_aggression_sellers(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) AS total_quantity, COUNT(*) AS total_count FROM trade_sellers;")
        record = cursor.fetchone()
        print("Total Sellers Quantity:", record[0])
        print("Total Sellers Count:", record[1])
        total_quantity = record[0]
        total_count = record[1]
        return total_quantity, total_count

    def delete_rows_by_time(self, table_name, timestamp_column, start_time, end_time):
        conn = self.connect()
        cursor = conn.cursor()
        delete_query = f"DELETE FROM {table_name} WHERE {timestamp_column} >= %s AND {timestamp_column} < %s;"
        cursor.execute(delete_query, (start_time, end_time))
        conn.commit()

    def insert_buy_signal(self, quantity, count):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO signals_buys (total_quantity, total_count) VALUES (%s, %s)",
                       (quantity, count))
        conn.commit()

    def insert_sells_signal(self, quantity, count):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO signals_sellers (total_quantity, total_quantity) VALUES (%s, %s)",
                       (quantity, count))
        conn.commit()
