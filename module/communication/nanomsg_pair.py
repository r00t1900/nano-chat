# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 17:58
# @Author  : Shek 
# @FileName: nanomsg_pair.py
# @Software: PyCharm

"""
Description:

A nanomsg-Pair mode class developed for a curses-based UI program

Simplified documentation:

This class can be divided into 3 parts:
configure, receive and send
part[self] has 3 function:
    start(protocol,addr,is_server), which used to create a nnpy.Socket(nnpy.AF_SP,nnpy.PAIR) object
    establish(protocol,addr,is_server), served for start()
    stop(), call nnpy.Socket.shutdown(who) and nnpy.Socket.close() to free socket and memory resources
part[recv] has 6 functions:
    start_recv_loop(chat_var): start a thread to feed data to outside variable "char_var", when flag_recv_enabled is 1
    stop_recv_loop(): set flag_recv_enabled to stop the thread
    disable_recv_loop():same as stop_recv_loop
    enable_recv_loop():set flag_recv_enabled to 1 so that thread can be start, should be called before start_recv_loop()
    is_recv_loop_enabled(): return value of flag_recv_enabled
part[send] has 1 function:
    send(text):use try-except to catch un-delivered signal(have to do so) with C_SEND_TIMEOUT defined in conf/config.py

Conclusion:

OK this library seems to be a little chaos because in part[recv] has duplicated function but I did not remove it. For
some reason is lazy but for some reason is that recently I was in a hurry for a examination so I left little time to
fulfill my code but left many other time for other parts of the program
Will update it soon.

Feb 13, 2020 by Shek
"""
import nnpy
import threading
from conf import config
from module.common import current_datetime


class PairObject:
    def __init__(self):
        self.flag_recv_enabled = False

        # variables defined here below just for coding convenience
        self.pair_socket, self.pair_socket_end_point = None, None
        # tell IDE its types
        assert isinstance(self.pair_socket, nnpy.Socket)
        assert isinstance(self.pair_socket_end_point, int)

    # SELF RELATED(REQUIRED)
    def start(self, protocol: str, addr: str, is_server: bool = True):
        # configure should be call first
        try:
            self.establish(protocol=protocol, addr=addr, is_server=is_server)
            return True, ''
        except Exception as e:
            return False, e

    def establish(self, protocol: str, addr: str, is_server: bool):
        """
        function that served for start(), run it directly may raise unexpected error
        :param protocol:
        :param addr:
        :param is_server:
        :return:
        """
        pair_socket = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
        # set send and recv timeout to 1s
        pair_socket.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, config.C_SEND_TIMEOUT)
        pair_socket.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, config.C_RECV_TIMEOUT)
        if is_server:  # run as server
            end_point = pair_socket.bind('{}://{}'.format(protocol, addr))
        else:  # run as client
            end_point = pair_socket.connect('{}://{}'.format(protocol, addr))
        self.pair_socket = pair_socket
        self.pair_socket_end_point = end_point  # for shutdown()

    def stop(self):
        """
        remember to shutdown and close if you do not use it anymore
        :return:
        """
        try:
            # who= endpoint (compatible API), references(https://nng.nanomsg.org/man/v1.1.0/nn_shutdown.3compat):
            # The nn_shutdown() shuts down the “endpoint” ep on the socket sock. This will stop the socket from either
            # accepting new connections, or establishing old ones. Additionally, any established connections associated
            # with ep will be closed.
            self.pair_socket.shutdown(who=self.pair_socket_end_point)
            self.pair_socket.close()
            print(config.C_COMM_MOD_STOP_SUCCEED_PREFIX.format(self.pair_socket_end_point))
        except Exception as e:
            print(config.C_COMM_MOD_STOP_FAILED_PREFIX.format(str(e)))

    # RECV RELATED
    def enable_recv_loop(self):
        self.flag_recv_enabled = True

    def disable_recv_loop(self):
        self.flag_recv_enabled = False

    def is_recv_loop_enabled(self):
        return self.flag_recv_enabled

    def __recv_loop(self, chat_var: list):
        while self.flag_recv_enabled:
            try:
                recv = self.pair_socket.recv()
                chat_var.append({'time': current_datetime(), 'message': recv.decode(config.DATA_ENCODING),
                                 'from': config.C_SEND_ROLE_NAME, 'role': config.C_FRIEND_ID})
            except nnpy.errors.NNError:
                continue

    def start_recv_loop(self, chat_var):
        threading.Thread(target=self.__recv_loop, args=(chat_var,)).start()

    def stop_recv_loop(self):
        self.disable_recv_loop()
        # print('recv thread stopped ...')

    # SEND RELATED
    def send(self, text: str):
        try:
            send_length = self.pair_socket.send(bytes(text, encoding=config.DATA_ENCODING))
            return True, send_length
        except nnpy.errors.NNError as e:
            return False, str(e)
