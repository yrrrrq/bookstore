import pytest
from fe import conf
from fe.access import deliver
from pymongo import MongoClient

class TestDelivery():
    @pytest.fixture(autouse=True)
    def setup(self):
        self.delivery = deliver.Deliver(conf.URL)
        self.store_id_receive = "valid_store123"
        self.order_id_receive = "valid_order123"
        self.buyer_id_receive = "valid_user123"

        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']
        self.user_collection = self.db['user']
        self.store_collection = self.db['store']
        self.user_store_collection = self.db['user_store']
        self.order_collection = self.db['new_order']

        self.order_collection.insert_one(
            {"order_id": self.order_id_receive, "store_id": self.store_id_receive, "user_id": self.buyer_id_receive,
             "status": 2})
        self.store_collection.insert_one({"store_id": self.store_id_receive})
        self.user_collection.insert_one({"user_id": self.buyer_id_receive})
        self.user_store_collection.insert_one({"store_id": self.store_id_receive, "user_id": self.buyer_id_receive})

    def test_receive_books_non_existing_user(self):
        non_existing_user_id = "non_existing_user_id"
        code, message = self.delivery.receive_books(non_existing_user_id, self.order_id_receive)
        assert code == 511  # Error code for non-existing user

    def test_receive_books_non_existing_order(self):
        non_existing_order = "non_existing_order"
        code, message = self.delivery.receive_books(self.buyer_id_receive, non_existing_order)
        assert code == 518  # Error code for invalid order

    def test_receive_books_invalid_order_status(self):
        invalid_order_status = "invalid_order_status"
        # make_order(valid_store_id, valid_order_id, valid_buyer_id)
        store_id = "invalid_store124"
        order_id = "invalid_order124"
        buyer_id = "invalid_user124"

        self.order_collection.insert_one(
            {"order_id": order_id, "store_id": store_id, "user_id": buyer_id, "status": invalid_order_status})
        self.store_collection.insert_one({"store_id": store_id})
        self.user_store_collection.insert_one({"store_id": store_id, "user_id": buyer_id})
        self.user_collection.insert_one({"user_id": buyer_id})
        code, message = self.delivery.receive_books(buyer_id,order_id)
        assert code == 522  # Error code for invalid order status


    def test_receive_books_success(self):
        code, message = self.delivery.receive_books(self.buyer_id_receive,self.order_id_receive)
        assert code == 200