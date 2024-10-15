import pytest

from fe.access.buyer import Buyer
from fe.access.book import Book
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid

class TestCancelOrder:
    buyer_id: str
    password: str
    seller_id: str
    store_id: str
    order_id: str
    buyer: Buyer


    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = "password_" + self.buyer_id
        self.seller_id = "test_find_orders_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_find_orders_store_id_{}".format(str(uuid.uuid1()))
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        yield

    def test_ok(self):
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200

    def test_authorization_error(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.cancel_order(self.order_id)
        assert code != 200

    def test_order_id_error(self):
        self.order_id = self.order_id + '_x'
        code = self.buyer.cancel_order(self.order_id)
        assert code != 200

