import logging
from pymongo import MongoClient
class Store:
    database: str
    client: MongoClient

    def __init__(self, db_path):
        self.database = "bookstore"
        self.client = MongoClient("mongodb://localhost:27017/")
        self.init_tables()

    def init_tables(self):
        try:
            """
            conn = self.get_db_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS store( "
                "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
                " PRIMARY KEY(store_id, book_id))"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order( "
                "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            conn.commit()
            """
            db = self.client[self.database]
            db.create_collection("user")
            db.create_collection("user_store")
            db.create_collection("store")
            db.create_collection("new_order")
            db.create_collection("new_order_detail")

            db["store"].create_index(
                [("book_info.book_intro", "text"), ("book_info.content", "text"), ("book_info.tags", "text"),
                 ("book_info.title", "text")])

        except Exception as e:
            logging.error(e)

    def get_db_conn(self):
        return self.client[self.database]


database_instance: Store = None
db_path = "mongodb://localhost:27017/"


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()