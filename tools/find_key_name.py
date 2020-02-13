# _*_coding:utf-8 _*_
# @Time    : 2020/2/12 13:40
# @Author  : Shek 
# @FileName: key_test_curses.py
# @Software: PyCharm
"""
press key on your keyboard and it returns you the key_name in curses along with its ASCII code
"""
import sys

sys.path.append('..')
from module.tools import print_key_name

if __name__ == '__main__':
    print_key_name()
