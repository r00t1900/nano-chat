# _*_coding:utf-8 _*_
# @Time    : 2020/2/6 11:42
# @Author  : Shek 
# @FileName: func.py
# @Software: PyCharm
from module.ui.curses import curses_boot_loader


def sub_cmd_bind(arguments):
    """
    function for sub command `bind`
    :param arguments:
    :return:
    """
    curses_boot_loader(arguments.protocol, arguments.addr, is_server=True)


def sub_cmd_connect(arguments):
    """
    function for sub command `connect`
    :param arguments:
    :return:
    """
    curses_boot_loader(arguments.protocol, arguments.addr, is_server=False)
