import sqlite3 as sqlite
import uuid
import json
import logging
import pymongo
from be.model import db_conn
from be.model import error
from pymongo import MongoClient
from be.model import time


class Buyer(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        self.user_collection = self.db['user']
        self.store_collection = self.db['store']
        self.user_store_collection = self.db['user_store']
        self.order_collection = self.db['new_order']
        self.order_detail_collection = self.db['new_order_detail']
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                #book_id = int(book_id)
                book = self.store_collection.find_one({"store_id": store_id, "book_id": str(book_id)})
                if not book:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = int(book.get("stock_level"))
                #price = int(book.get("price", 0))
                price = int(book["book_info"]["price"])
                #print(price)

                if int(stock_level) < int(count):
                    return error.error_stock_level_low(book_id) + (order_id,)

                self.store_collection.update_one(
                    {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}}
                )

                self.order_detail_collection.insert_one({
                    "order_id": uid,
                    "status": 0,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })

            self.order_collection.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "status": 0
            })
            order_id = uid
            code, _ = time.add_unpaid_order(order_id)
            print(code)
            print(time.unpaid_orders)


        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        #conn = self.conn
        try:
            order = self.order_collection.find_one({"order_id": order_id})
            if not order:
                return error.error_invalid_order_id(order_id)
            buyer_id = order["user_id"]
            store_id = order["store_id"]

            print(time.unpaid_orders)
            print(time.check_order_time(order_id))
            if time.check_order_time(order_id) == False:
                print("超时咯")
                time.delete_unpaid_order(order_id)
                print(time.unpaid_orders)
                return error.error_invalid_order_id(order_id)

            if buyer_id != user_id:
                return error.error_authorization_fail()

            buyer = self.user_collection.find_one({"user_id": buyer_id})
            if not buyer:
                return error.error_non_exist_user_id(buyer_id)

            balance = buyer["balance"]
            if password != buyer["password"]:
                return error.error_authorization_fail()

            seller = self.user_store_collection.find_one({"store_id": store_id})
            if not seller:
                return error.error_non_exist_store_id(store_id)

            seller_id = seller["user_id"]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            total_price = 0
            order_details = self.order_detail_collection.find({"order_id": order_id})

            for detail in order_details:
                count = detail["count"]
                price = detail["price"]
                total_price += price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            balance -= total_price

            if balance < 0:
                return error.error_not_sufficient_funds(order_id)

            #balance += total_price
            #if balance <= 0:
            #    return error.error_non_exist_user_id(buyer_id)

            #self.order_collection.delete_one({"order_id": order_id})
            #self.order_detail_collection.delete_many({"order_id": order_id})

            self.user_collection.update_one({"user_id": user_id}, {'$set': {"balance": balance}})
            self.user_collection.update_one({"user_id": seller_id}, {'$inc': {"balance": total_price}})

            self.order_collection.update_one({"order_id": order_id}, {'$set':{"status": 1}})
            self.order_detail_collection.update_many({"order_id":order_id}, {'$set': {"status": 1}})

            time.delete_unpaid_order(order_id)

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user = self.user_collection.find_one({"user_id": user_id})
            if not user:
                return error.error_authorization_fail()

            if user["password"] != password:
                return error.error_authorization_fail()

            result = self.user_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": int(add_value)}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def find_orders(self, user_id: str):
        try:
            user = self.user_collection.find_one({"user_id": user_id})
            if not user:
                return error.error_authorization_fail()+ ("",)

            result = self.order_collection.find({"user_id": user_id})
            order_list = []
            for each in result:
                order_Id = each["order_id"]
                order = self.order_detail_collection.find_one({"order_id": order_Id})
                #print(order["order_id"])
                order_data = {
                    "order_id": order["order_id"],
                    "book_id": order["book_id"],
                    "count": order["count"],
                    "price": order["price"],
                    "status": order["status"]
                }
                #print(order_Id)
                #print(order)
                #print(order_data)
                order_list.append(order_data)
                #print(order_list)

        except sqlite.Error as e:
            return 528,"{}".format(str(e))
        except BaseException as e:
            return 530,"{}".format(str(e))
        return 200, "ok", order_list

    def cancel_order(self, user_id: str, password: str, order_id: str):
        try:
            user = self.user_collection.find_one({"user_id": user_id})
            if not user:
                return error.error_authorization_fail()
            if user["password"] != password:
                return error.error_authorization_fail()

            order = self.order_collection.find_one({"order_id": order_id})
            if not order:
                return error.error_invalid_order_id(order_id)
            user_Id = order["user_id"]
            order_Id = order['order_id']
            store_Id = order['store_id']

            #store = self.store_collection.find_one({"store_id": store_Id})
            order_details = self.order_detail_collection.find({"order_id": order_id})

            for each in order_details:
                book_Id = each['book_id']
                Count = each['count']
                Price = each['price']
                self.store_collection.update_one({"store_id": store_Id, "book_id": book_Id}, {'$inc':{"count": Count}})
                self.user_collection.update_one({"user_id": user_Id}, {'$inc':{"balance": Price}})

            self.order_detail_collection.update_one({"order_id": order_id}, {'$set': {"status": 4}})
            self.order_collection.update_one({"order_id": order_id}, {'$set': {"status": 4}})

            time.delete_unpaid_order(order_Id)

        except sqlite.Error as e:
            return 528,"{}".format(str(e))
        except BaseException as e:
            return 530,"{}".format(str(e))
        return 200, "ok"

