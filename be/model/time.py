from pymongo import MongoClient
import datetime
import time

client = MongoClient('localhost', 27017)
db = client['bookstore']
order_collection = db['new_order']
order_detail_collection = db['new_order_detail']

def get_time_stamp():
    cur_time_stamp = time.time()
    return cur_time_stamp

time_limit = 30
unpaid_orders = {}

def add_unpaid_order(order_id):
    unpaid_orders[order_id] = get_time_stamp()
    return 200, "ok"

def delete_unpaid_order(order_id):
    try:
        unpaid_orders.pop(order_id)
        order_collection.update_one({"order_id": order_id}, {'$set':{"status": 4}})
        order_detail_collection.update_many({"order_id": order_id}, {'$set':{"status": 4}})
    except BaseException as e:
        return 530,"{}".format(str(e))
    return 200, "ok"

def check_order_time(order_id):
    cur_time = get_time_stamp()
    order_time = unpaid_orders[order_id]
    time_exist = float(cur_time) - float(order_time)
    if float(time_exist) > float(time_limit):
        return False
    else:
        return True

def time_exceed_delete():
    del_tmp = []
    for (oid, tim) in unpaid_orders.items():
        if check_order_time(tim) == False:
            del_tmp.append(oid)
    for oid in del_tmp:
        delete_unpaid_order(oid)

