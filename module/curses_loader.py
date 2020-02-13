# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 20:48
# @Author  : Shek 
# @FileName: bootloader.py
# @Software: PyCharm
from module.pair import PairObject
from module.curses import curses_main_for_wrapper
from conf import config
from curses import wrapper


def curses_boot_loader(protocol: str, addr: str, is_server: bool):
    chat_logs = []
    comm_type = PairObject()
    comm_conf_status, comm_err_inf = comm_type.configure(protocol, addr, is_server)
    if comm_conf_status:
        comm_type.enable_recv_loop()
        comm_type.start_recv_loop(chat_var=chat_logs)
        wrapper(curses_main_for_wrapper, comm_type, chat_logs)
    else:
        print('{}\n{}'.format(config.C_WRAPPER_STOPPED_WITH_FAILURE_TEXT_SUFFIX, comm_err_inf))
