import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from pymongo import MongoClient


class Delivery(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        self.user_collection = self.db['user']
        self.store_collection = self.db['store']
        self.user_store_collection = self.db['user_store']
        self.order_collection = self.db['new_order']
        self.order_detail_collection = self.db['new_order_detail']
        db_conn.DBConn.__init__(self)

    def send_books(self,  store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                #print("store_id_exist")
                return error.error_non_exist_store_id(store_id)
            if not self.order_id_exist(order_id):  # 增加order_id不存在的错误处理
                return error.error_invalid_order_id(order_id)
            #print("here")
            order = self.order_collection.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            #print("there")
            status = order.get("status")
            if status != 1:
                return error.error_invalid_order_status(order_id)
            self.order_collection.update_one({"order_id": order_id}, {"$set": {"status": 2}})
            return 200, "ok"

        except Exception as e:
            return 530, "{}".format(str(e)), ""

    def receive_books(self, user_id: str, order_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                print("user—exist",user_id)
                logging.error("User ID does not exist: {}".format(user_id))
                return error.error_non_exist_user_id(user_id)

            if not self.order_id_exist(order_id):
                print("order_exit",order_id)
                logging.error("Order ID does not exist: {}".format(order_id))
                return error.error_invalid_order_id(order_id)

            order = self.order_collection.find_one({"order_id": order_id})
            if order is None:
                logging.error("Order not found for ID: {}".format(order_id))
                print("order not found")
                return error.error_invalid_order_id(order_id)

            buyer = order.get("user_id")
            store = order.get("store_id")
            status = order.get("status")

            if buyer != user_id:
                return error.error_authorization_fail()

            if status != 2:
                return error.error_invalid_order_status(order_id)

            store_f = self.user_store_collection.find_one({"store_id": store})
            if store_f is None:
                logging.error("Store not found for ID: {}".format(store))
                return error.error_non_exist_store_id(store)

            seller = store_f.get("user_id")
            if not self.user_id_exist(seller):
                logging.error("Seller not found for ID: {}".format(seller))
                return error.error_non_exist_user_id(seller)

            self.order_collection.update_one(
                {"order_id": order_id},
                {"$set": {"status": 3}}
            )
            return 200, "ok"
        except Exception as e:
            logging.error("Error in receive_books: {}".format(str(e)))
            return 530, "{}".format(str(e))