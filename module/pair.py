# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 17:58
# @Author  : Shek 
# @FileName: pair.py
# @Software: PyCharm
import nnpy
import threading
import datetime
from conf import config


def current_datetime(format_str: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format_str)


class PairObject:
    def __init__(self):
        # self.pair_socket = nnpy.Socket  # has not been configured yet, just for debugging convenience
        # self.pair_socket = nnpy.Socket()  # has not been configured yet, just for debugging convenience
        self.flag_recv_enabled = False

    def configure(self, protocol: str, addr: str, is_server: bool = True):
        # configure should be call first
        try:
            pair_socket = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
            # set send and recv timeout to 1s
            pair_socket.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, config.C_SEND_TIMEOUT)
            pair_socket.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, config.C_RECV_TIMEOUT)
            if is_server:  # run as server
                pair_socket.bind('{}://{}'.format(protocol, addr))
            else:  # run as client
                pair_socket.connect('{}://{}'.format(protocol, addr))
            self.pair_socket = pair_socket
            return True, ''
        except Exception as e:
            return False, e

    def enable_recv_loop(self):
        self.flag_recv_enabled = True

    def disable_recv_loop(self):
        self.flag_recv_enabled = False

    def is_recv_loop_enabled(self):
        return self.flag_recv_enabled

    def recv_loop(self, chat_var: list):
        while self.flag_recv_enabled:
            try:
                recv = self.pair_socket.recv()
                chat_var.append({'time': current_datetime(), 'message': recv.decode(config.DATA_ENCODING),
                                 'from': config.C_SEND_ROLE_NAME, 'role': config.C_FRIEND_ID})
            except nnpy.errors.NNError:
                continue

    def start_recv_loop(self, chat_var):
        threading.Thread(target=self.recv_loop, args=(chat_var,)).start()

    def stop_recv_loop(self):
        self.flag_recv_enabled = False
        # print('recv thread stopped ...')

    def send(self, text: str):
        try:
            send_length = self.pair_socket.send(bytes(text, encoding='utf-8'))
            return True, send_length
        except nnpy.errors.NNError as e:
            return False, str(e)
