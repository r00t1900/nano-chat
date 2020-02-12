# _*_coding:utf-8 _*_
# @Time    : 2020/2/12 13:40
# @Author  : Shek 
# @FileName: key_test_curses.py
# @Software: PyCharm
import curses
from curses import wrapper


def main(std_scr):
    row = 0
    while True:
        ch = std_scr.getch()
        std_scr.move(row, 0)
        std_scr.clrtoeol()
        std_scr.addstr(row, 0, '{}:{}'.format(ch, curses.keyname(ch)))
        row += 1


wrapper(main)
