# _*_coding:utf-8 _*_
# @Time    : 2020/2/9 12:26
# @Author  : Shek 
# @FileName: pair_recv.py
# @Software: PyCharm

import nnpy
import sqlite3
import _md5
import datetime
from Crypto.Cipher import AES
import base64


class Database:
    def __init__(self, db_filename: str):
        self.filename = db_filename

    @staticmethod
    def __dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_connection(self):
        self.db = sqlite3.connect(self.filename)
        self.db.row_factory = self.__dict_factory
        return self.db


class Chat:
    def __init__(self, conn_obj):
        self.hash_encoding = 'utf-8'
        self.db = conn_obj
        self.user = {}
        self.friend = {}
        pass

    @staticmethod
    def __now():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def __hash(self, text: str):
        return _md5.md5(text.encode(self.hash_encoding)).hexdigest()

    def ping_friend(self, addr: str, friend_username: str):
        pass

    def pinged_by_friend(self):
        pass

    def receive_message(self):
        pass

    def send_message(self):
        pass

    def update_message_delivered_status(self):
        pass

    def user_login(self, username: str, password: str, verbose: bool = True):
        if self.is_user_exists(username):
            if self.is_user_password_matched(username, password):
                if verbose:
                    print('login as {} :)'.format(username))
                self.user = self.get_user_information(username, password)
            else:
                if verbose:
                    print('login failed :(')
        else:
            print('account {} does not exist yet'.format(username))

    def user_register(self, username: str, password: str):
        password = self.__hash(password)
        time_joined = self.__now()
        if self.is_user_exists(username):
            print('username {} exists already'.format(username))
            return False
        self.db.execute('insert into t_user (username, password, time_joined) '
                        'values (?,?,?)', (username, password, time_joined,))
        self.db.commit()
        print('account {} create successfully'.format(username))
        return True

    def get_user_information(self, username: str, password: str):
        password = self.__hash(password)
        result = self.db.execute('select * from t_user where username=? and password=?', (username, password,))
        result = result.fetchall()
        return result[0]

    def is_user_password_matched(self, username: str, password: str):
        password = self.__hash(password)
        result = self.db.execute('select * from t_user where username=? and password=?', (username, password,))
        result = result.fetchall()
        if len(result):
            return True
        else:
            return False

    def is_user_exists(self, username: str):
        result = self.db.execute('select * from t_user where username=?', (username,))
        result = result.fetchall()
        if len(result):
            return True
        else:
            return False


db = Database('data.db')
conn = db.get_connection()
chat = Chat(conn)
chat.user_register('vflanker', '123456')
chat.user_login('vflanker', '123456')
