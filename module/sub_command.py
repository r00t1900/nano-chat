# _*_coding:utf-8 _*_
# @Time    : 2020/2/6 11:42
# @Author  : Shek 
# @FileName: func.py
# @Software: PyCharm
from module.pair import PairObject
from module.curses import curses_main_for_wrapper
from curses import wrapper
from conf import config


def sub_cmd_bind(arguments):
    chat_logs = []
    comm_type = PairObject()
    comm_conf_status, comm_err_inf = comm_type.configure(arguments.protocol, arguments.addr, is_server=True)
    if comm_conf_status:
        comm_type.enable_recv_loop()
        comm_type.start_recv_loop(chat_var=chat_logs)
        wrapper(curses_main_for_wrapper, comm_type, chat_logs)  # pair->pair_obj of curses_main_for_wrapper
        print(config.C_WRAPPER_STOPPED_HINT_TEXT)
    else:
        print('{}\n{}'.format(config.C_WRAPPER_STOPPED_WITH_FAILURE_TEXT_SUFFIX, comm_err_inf))


def sub_cmd_connect(arguments):
    chat_logs = []
    comm_type = PairObject()
    comm_conf_status, comm_err_inf = comm_type.configure(arguments.protocol, arguments.addr, is_server=False)
    if comm_conf_status:
        comm_type.enable_recv_loop()
        comm_type.start_recv_loop(chat_var=chat_logs)
        wrapper(curses_main_for_wrapper, comm_type, chat_logs)
        print(config.C_WRAPPER_STOPPED_HINT_TEXT)
    else:
        print('{}\n{}'.format(config.C_WRAPPER_STOPPED_WITH_FAILURE_TEXT_SUFFIX, comm_err_inf))
