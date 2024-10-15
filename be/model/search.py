from be.model import error
from be.model import db_conn
from flask import jsonify


class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_only_store(self,
                          choose: int,
                          store_id: str,
                          keyword: str,
                          page: int,
                          limit: int):
        try:
            if not self.store_id_exist(store_id):
                print("hihi can u get, can u learn that u can't get store_id")
                return error.error_non_exist_store_id(store_id) + ("",)

            choose = int(choose)
            keyword_list = keyword.split()

            if choose == 0:  # content
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.content": {"$regex": keyword}})
                result = self.conn["store"].find({"$and": [{"store_id": store_id},
                                                           {"$or": regex_filters}]})
                count = self.conn["store"].count_documents({"$and": [{"store_id": store_id},
                                                                     {"$or": regex_filters}]})
            elif choose == 1:  # tag
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.tags": {"$regex": keyword}})
                result = self.conn["store"].find({"$and": [{"store_id": store_id},
                                                           {"$or": regex_filters}]})
                count = self.conn["store"].count_documents({"$and": [{"store_id": store_id},
                                                                     {"$or": regex_filters}]})
            elif choose == 2:  # title
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.title": {"$regex": keyword}})
                result = self.conn["store"].find({"$and": [{"store_id": store_id},
                                                           {"$or": regex_filters}]})
                count = self.conn["store"].count_documents({"$and": [{"store_id": store_id},
                                                                     {"$or": regex_filters}]})

            elif choose == 3:  # book_intro
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.book_intro": {"$regex": keyword}})
                result = self.conn["store"].find({"$and": [{"store_id": store_id},
                                                           {"$or": regex_filters}]})
                count = self.conn["store"].count_documents({"$and": [{"store_id": store_id},
                                                                     {"$or": regex_filters}]})

            elif choose == 4:  # book_intro
                result = self.conn["store"].find({"$and": [{"store_id": store_id},
                                                           {"$text": {"$search": keyword}}]})  # 全文索引
                count = self.conn["store"].count_documents({"$and": [{"store_id": store_id},
                                                                     {"$text": {"$search": keyword}}]})

            """
            elif choose == 4:#book_intro

                result = self.conn["store"].find({"$and": [{"store_id": store_id},
                                                           ({"$or": [{"book_info.book_intro": {"$regex": keyword}},
                                                                     {"book_info.title": {"$regex": keyword}},
                                                                     {"book_info.tags": {"$regex": keyword}},
                                                                     {"book_info.content": {"$regex": keyword}}]})]})
                # 匹配商店，正则化匹配content
                count = self.conn["store"].count_documents({"$and": [{"store_id": store_id},
                                                           ({"$or": [{"book_info.book_intro": {"$regex": keyword}},
                                                                     {"book_info.title": {"$regex": keyword}},
                                                                     {"book_info.tags": {"$regex": keyword}},

            """

            print(count)
            if count == 0:
                print("can u know count==0")
                return error.error_not_book_in_this_store(store_id) + ("",)

            page = int(page)
            limit = int(limit)

            skip = (page - 1) * limit

            results = result.skip(skip).limit(limit)

            books = []

            for book in results:
                book_info = book["book_info"]
                book_data = {
                    "id": book_info["id"],
                    "title": book_info["title"],
                    "author": book_info["author"],
                    "tags": "\n".join(book_info["tags"]),
                    "publisher": book_info["publisher"],
                    "original_title": book_info["original_title"],
                    "pub_year": book_info["pub_year"],
                    "pages": book_info["pages"],
                    "binding": book_info["binding"],
                    "author_intro": book_info["author_intro"],
                    "content": book_info["content"]
                }
                # 需要将book_info存储为正确的格式，传给view/search
                books.append(book_data)

            print(books)

        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "OK", books

    def search_all(self,
                   choose: int,
                   keyword: str,
                   page: int,
                   limit: int):
        try:
            choose = int(choose)
            keyword_list = keyword.split()

            if choose == 0:  # content
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.content": {"$regex": keyword}})
                result = self.conn["store"].find({"$or": regex_filters})
                count = self.conn["store"].count_documents({"$or": regex_filters})

            elif choose == 1:  # tags
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.tags": {"$regex": keyword}})
                result = self.conn["store"].find({"$or": regex_filters})
                count = self.conn["store"].count_documents({"$or": regex_filters})
            elif choose == 2:  # title
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.title": {"$regex": keyword}})
                result = self.conn["store"].find({"$or": regex_filters})
                count = self.conn["store"].count_documents({"$or": regex_filters})
            elif choose == 3:  # book_intro
                regex_filters = []
                for keyword in keyword_list:
                    regex_filters.append({"book_info.book_intro": {"$regex": keyword}})
                result = self.conn["store"].find({"$or": regex_filters})
                count = self.conn["store"].count_documents({"$or": regex_filters})
            elif choose == 4:  # book_intro
                result = self.conn["store"].find({"$text": {"$search": keyword}})  # 全文索引
                count = self.conn["store"].count_documents({"$text": {"$search": keyword}})

            """
            elif choose == 4:  # book_intro
                result = self.conn["store"].find({"$or": [{"book_info.book_intro": {"$regex": keyword}}, {"book_info.title": {"$regex": keyword}}, {"book_info.tags": {"$regex": keyword}}, {"book_info.content": {"$regex": keyword}}]})  # 匹配商店，正则化匹配content
                count = self.conn["store"].count_documents({"$or": [{"book_info.book_intro": {"$regex": keyword}}, {"book_info.title": {"$regex": keyword}}, {"book_info.tags": {"$regex": keyword}}, {"book_info.content": {"$regex": keyword}}]})
            """

            print(count)
            if count == 0:
                print("can u know count==0")
                return error.error_not_book_which_u_want() + ("",)

            page = int(page)
            limit = int(limit)

            skip = (page - 1) * limit

            results = result.skip(skip).limit(limit)

            books = []

            for book in results:
                book_info = book["book_info"]
                book_data = {
                    "id": book_info["id"],
                    "title": book_info["title"],
                    "author": book_info["author"],
                    "tags": "\n".join(book_info["tags"]),
                    "publisher": book_info["publisher"],
                    "original_title": book_info["original_title"],
                    "pub_year": book_info["pub_year"],
                    "pages": book_info["pages"],
                    "binding": book_info["binding"],
                    "author_intro": book_info["author_intro"],
                    "content": book_info["content"]
                }
                # 需要将book_info存储为正确的格式，传给view/search
                books.append(book_data)
            print(books)

        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "OK", books
