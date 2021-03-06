# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 20:39
# @Author  : Shek 
# @FileName: tools.py
# @Software: PyCharm
import curses
from conf import config
from curses import wrapper
from modules.ui.curses import boot_loader4curses


def print_key_name():
    """
    press key on your keyboard and it returns you the key_name in curses along with its ASCII code
    :return:
    """

    def main(std_scr):
        row = 0
        std_scr.addstr(row, 0, ' Get key name by pressing key, Ctrl-C to exit the program')
        std_scr.refresh()
        row += 1
        std_scr.move(row, 0)
        while True:
            ch = std_scr.getch()
            std_scr.clrtoeol()
            std_scr.addstr(row, 0, '{}:{}'.format(ch, curses.keyname(ch)))
            row += 1
            std_scr.move(row, 0)

    wrapper(main)


def curse_ui_test_server():
    """
    test curses UI with default config in server mode
    :return:
    """
    boot_loader4curses(config.PROTOCOL, config.BIND_ADDR, is_server=True)  # test as a server node


def curse_ui_test_client():
    """
    test curses UI with default config in client mode
    :return:
    """
    boot_loader4curses(config.PROTOCOL, config.CONNECT_ADDR, is_server=False)  # test as a client node
