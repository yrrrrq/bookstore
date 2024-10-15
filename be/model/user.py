import jwt
import time
import logging
import sqlite3 as sqlite

import pymongo

from be.model import error
from be.model import db_conn
from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):

        terminal = "terminal_{}".format(str(time.time()))
        token = jwt_encode(user_id, terminal)
        '''
        self.conn.execute(
            "INSERT into user(user_id, password, balance, token, terminal) "
            "VALUES (?, ?, ?, ?, ?);",
            (user_id, password, 0, token, terminal),
        )
        self.conn.commit()
        '''
        result = self.conn["user"].find({"user_id": user_id})
        if len(list(result)) == 0:
            self.conn["user"].insert_one({"user_id": user_id, "password": password, "balance": 0, "token": token, "terminal": terminal})
        else:
            return error.error_exist_user_id(user_id)

        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        '''
        cursor = self.conn.execute("SELECT token from user where user_id=?", (user_id,))
        row = cursor.fetchone()
        if row is None:
            return error.error_authorization_fail()
        db_token = row[0]
        '''
        result = self.conn["user"].find_one({"user_id": user_id})
        if not result:
            return error.error_authorization_fail()

        db_token = result['token']

        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        '''
        cursor = self.conn.execute(
            "SELECT password from user where user_id=?", (user_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return error.error_authorization_fail()

        if password != row[0]:
            return error.error_authorization_fail()
        '''
        result = self.conn["user"].find_one({"user_id": user_id})
        if not result:
            return error.error_authorization_fail()

        if password != result["password"]:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            '''
            cursor = self.conn.execute(
                "UPDATE user set token= ? , terminal = ? where user_id = ?",
                (token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_authorization_fail() + ("",)
            self.conn.commit()
            '''
            condition = {"user_id": user_id}
            result = self.conn["user"].update_one(condition, {'$set': {"token": token, "terminal": terminal}})
            if not result:
                return error.error_authorization_fail() + ("",)
            # self.conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            '''
            cursor = self.conn.execute(
                "UPDATE user SET token = ?, terminal = ? WHERE user_id=?",
                (dummy_token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_authorization_fail()
            self.conn.commit(
            '''
            condition = {"user_id": user_id}
            result = self.conn["user"].update_one(condition,
                                         {'$set': {"token": dummy_token, "terminal": terminal}})
            if result.modified_count == 0:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            '''
            cursor = self.conn.execute("DELETE from user where user_id=?", (user_id,))
            if cursor.rowcount == 1:
                self.conn.commit()
            else:
                return error.error_authorization_fail()
            '''
            condition = {"user_id": user_id}
            result = self.conn["user"].delete_one(condition)
            if result.deleted_count != 1:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            '''
            cursor = self.conn.execute(
                "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?",
                (new_password, token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_authorization_fail()
            self.conn.commit()
            '''
            condition = {"user_id": user_id}
            result = self.conn["user"].find_one(condition)
            if result:
                self.conn["user"].update_one(condition,
                                             {'$set': {"password": new_password, "token": token, "terminal": terminal}})
            else:
                return error.error_authorization_fail()
            # conn.commit()
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"