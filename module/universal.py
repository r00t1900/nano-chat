# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 19:57
# @Author  : Shek 
# @FileName: common.py
# @Software: PyCharm
from conf import config
import datetime


def cn_count(text: str, code_all=None):
    if code_all is None:
        code_all = config.CODE_SETS
    count = 0
    for code_range in code_all:
        for ch in text:
            if code_range[0] <= ch <= code_range[1]:
                count += 1
    return count


def current_datetime(format_str: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format_str)
