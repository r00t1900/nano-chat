# _*_coding:utf-8 _*_
# @Time    : 2020/2/6 11:42
# @Author  : Shek 
# @FileName: func.py
# @Software: PyCharm
from modules.ui.curses import boot_loader4curses


def sub_cmd_bind(arguments):
    """
    function for sub command `bind`
    :param arguments:
    :return:
    """
    boot_loader4curses(arguments.protocol, arguments.addr, is_server=True)


def sub_cmd_connect(arguments):
    """
    function for sub command `connect`
    :param arguments:
    :return:
    """
    boot_loader4curses(arguments.protocol, arguments.addr, is_server=False)
