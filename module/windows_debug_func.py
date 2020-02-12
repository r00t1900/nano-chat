# _*_coding:utf-8 _*_
# @Time    : 2020/2/12 20:59
# @Author  : Shek 
# @FileName: windows_debug_func.py
# @Software: PyCharm
import curses
from curses import wrapper


def tool_key_name():
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
