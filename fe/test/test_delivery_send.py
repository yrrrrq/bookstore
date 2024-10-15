import pytest
from fe import conf
from fe.access import deliver
from pymongo import MongoClient

class TestDelivery():
    @pytest.fixture(autouse=True)
    def setup(self):
        self.delivery = deliver.Deliver(conf.URL)
        self.store_id_send = "valid_store124"
        self.order_id_send = "valid_order124"
        self.buyer_id_send = "valid_user124"

        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        self.user_collection = self.db['user']
        self.store_collection = self.db['store']
        self.user_store_collection = self.db['user_store']
        self.order_collection = self.db['new_order']

        self.order_collection.insert_one(
            {"order_id": self.order_id_send, "store_id":self.store_id_send, "user_id":self.buyer_id_send, "status": 1})
        self.store_collection.insert_one({"store_id":self.store_id_send})
        self.user_store_collection.insert_one({"store_id":self.store_id_send,"user_id":self.buyer_id_send})
        self.user_collection.insert_one({"user_id": self.buyer_id_send})

    def test_send_books_non_existing_store(self):
        non_existing_store_id = "non_existing_store_id"
        code, message = self.delivery.send_books(non_existing_store_id, self.order_id_send)
        assert code == 513  # Error code for non-existing store


    def test_send_books_non_existing_order(self):
        non_existing_order_id = "non_existing_order_id"
        code, message = self.delivery.send_books(self.store_id_send, non_existing_order_id)
        assert code == 518  # Error code for invalid order

    def test_send_books_invalid_order_status(self):
        invalid_order_status = "invalid_order_status_id"
        store_id = "invalid_store124"
        order_id = "invalid_order124"
        buyer_id = "invalid_user124"

        self.order_collection.insert_one(
            {"order_id": order_id, "store_id": store_id, "user_id": buyer_id, "status": invalid_order_status})
        self.store_collection.insert_one({"store_id": store_id})
        self.user_store_collection.insert_one({"store_id": store_id, "user_id": buyer_id})
        self.user_collection.insert_one({"user_id": buyer_id})
        code, message = self.delivery.send_books(store_id, order_id)
        assert code == 522  # Error code for invalid order status

    def test_send_books_success(self):
        code, message = self.delivery.send_books(self.store_id_send, self.order_id_send)
        assert code == 200