# _*_coding:utf-8 _*_
# @Time    : 2020/2/11 12:00
# @Author  : Shek 
# @FileName: cursesUI.py
# @Software: PyCharm

from curses import wrapper
from module.pair import PairObject
from module.curses import curses_main_for_wrapper
import config

chat_logs = []
comm_type = PairObject()
comm_conf_status, comm_err_inf = comm_type.configure(config.PROTOCOL, config.BIND_ADDR, is_server=True)
if comm_conf_status:
    comm_type.enable_recv_loop()
    comm_type.start_recv_loop(chat_var=chat_logs)
    wrapper(curses_main_for_wrapper, comm_type, chat_logs)
else:
    print('{}\n{}'.format(config.C_WRAPPER_STOPPED_WITH_FAILURE_TEXT_SUFFIX, comm_err_inf))
