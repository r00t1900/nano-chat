# _*_coding:utf-8 _*_
# @Time    : 2020/2/6 11:42
# @Author  : Shek 
# @FileName: func.py
# @Software: PyCharm
from module.pair import PairObject
from module.curses import curses_main_for_wrapper
from curses import wrapper


def sub_cmd_bind(arguments):
    chat_logs = []
    pair = PairObject()
    pair_conf_status, err_inf = pair.configure(arguments.protocol, arguments.addr, is_server=True)
    if pair_conf_status:
        pair.enable_recv_loop()
        pair.start_recv_loop(chat_var=chat_logs)
        wrapper(curses_main_for_wrapper, pair, chat_logs)  # pair->pair_obj of curses_main_for_wrapper
        print('all stopped.')
    else:
        print('init failed because:\n{}'.format(err_inf))


def sub_cmd_connect(arguments):
    chat_logs = []
    pair = PairObject()
    pair_conf_status, err_inf = pair.configure(arguments.protocol, arguments.addr, is_server=False)  # is_server:0
    if pair_conf_status:
        pair.enable_recv_loop()
        pair.start_recv_loop(chat_var=chat_logs)
        wrapper(curses_main_for_wrapper, pair, chat_logs)
        print('all stopped.')
    else:
        print('init failed because:\n'.format(err_inf))
