# _*_coding:utf-8 _*_
# @Time    : 2020/2/13 19:57
# @Author  : Shek 
# @FileName: common.py
# @Software: PyCharm
from conf import config
import datetime


def cn_count(text: str, code_sets: list = None):
    """
    count special characters(in here the code-set is for chinese characters and commas)
    :param text: string to be count
    :param code_sets: ch code's ranges' set
    :return: the count
    """
    if code_sets is None:
        code_sets = config.CODE_SETS
    count = 0
    for code_range in code_sets:
        for ch in text:
            if code_range[0] <= ch <= code_range[1]:
                count += 1
    return count


def current_datetime(format_str: str = '%Y-%m-%d %H:%M:%S'):
    """
    return the datetime string in format of the variable `format_str`
    :param format_str: datetime format string
    :return: formatted datetime string
    """
    return datetime.datetime.now().strftime(format_str)
