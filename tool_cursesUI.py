# _*_coding:utf-8 _*_
# @Time    : 2020/2/11 12:00
# @Author  : Shek 
# @FileName: cursesUI.py
# @Software: PyCharm

from curses import wrapper
from module.windows import *
from module.pair import PairObject

chat_logs, debug_logs = [], []
pair = PairObject()
pair_conf_status, err_inf = pair.configure('tcp', '*:4000', is_server=True)
if pair_conf_status:
    pair.enable_recv_loop()
    pair.start_recv_loop(chat_var=chat_logs)
    wrapper(curses_main_for_wrapper, pair, chat_logs, debug_logs)
else:
    print('init failed because:\n'.format(err_inf))
