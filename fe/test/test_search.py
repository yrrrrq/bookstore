import pytest
from fe.access.search import Search
from fe import conf
from fe.access.new_seller import register_new_seller
import uuid
from fe.access import book

class TestSearchBooks:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        #self.store_id = "test_add_book_stock_level1_store_d986a1b8-7bca-11ee-a692-82dcc49d4580"
        self.seller_id = "test_search_books_user_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 10)
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        self.keyword = "撒哈拉 三毛"
        self.page = 1
        self.limit = 10
        self.store = Search(conf.URL)
        yield

    def test_search_only(self):
        for i in range(5):
            code, message, result = self.store.search_only_store(i, self.store_id, self.keyword, self.page, self.limit)
            assert code == 200

    def test_search_all(self):
        for i in range(5):
            code, message, result = self.store.search_all(i, self.keyword, self.page, self.limit)
            assert code == 200

    def test_search_one_word_not_found(self):
        for i in range(5):
            code, message, result = self.store.search_all(i, "呜呜 撒哈拉", self.page, self.limit)
            assert code == 200

    def test_nonbook_this_store(self):
        for i in range(5):
            code, message, result = self.store.search_only_store(i, self.store_id, "呜呜x_x", self.page, self.limit)
            assert code == 520

    def test_nonbook_all_store(self):
        for i in range(5):
            code, message, result = self.store.search_all(i, "呜呜x_x", self.page, self.limit)
            assert code == 521

    def test_nonstore(self):
        for i in range(5):
            code, message, result = self.store.search_only_store(0,  "store_id", self.keyword, self.page, self.limit)
            assert code == 513
