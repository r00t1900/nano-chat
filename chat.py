# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 18:41
# @Author  : Shek 
# @FileName: chat.py
# @Software: PyCharm
import argparse
from module.sub_command import *
from conf import config

parser = argparse.ArgumentParser(description=config.PROGRAM_DESCRIPTION)
subparsers = parser.add_subparsers()

# command 'bind'
cmd_bind = subparsers.add_parser('bind', help=config.H_BIND)
cmd_bind.add_argument('protocol', action='store', nargs='?', default=config.PROTOCOL, help=config.H_BIND_PROTOCOL)
cmd_bind.add_argument('addr', action='store', nargs='?', default=config.BIND_ADDR, help=config.H_BIND_ADDR)
cmd_bind.set_defaults(func=sub_cmd_bind)

# command 'connect'
cmd_connect = subparsers.add_parser('connect', help=config.H_CONNECT)
cmd_connect.add_argument('protocol', action='store', nargs='?', default=config.PROTOCOL, help=config.H_CONNECT_PROTOCOL)
cmd_connect.add_argument('addr', action='store', nargs='?', default=config.CONNECT_ADDR, help=config.H_CONNECT_ADDR)
cmd_connect.add_argument('--subscribe', action='store', nargs='?', default=config.CONNECT_SUBSCRIBE,
                         help=config.H_CONNECT_SUBSCRIBE)
cmd_connect.add_argument('--keep-alive', action='store_true', help=config.H_CONNECT_KEEP_ALIVE)
cmd_connect.set_defaults(func=sub_cmd_connect)

args = parser.parse_args()  # 处理输入的参数
if not hasattr(args, 'func'):
    # 无参数时跳转到-h，否则会提示 namespace object has not attribute 'func'，故这里用hasattr()判断
    args = parser.parse_args(['-h'])
args.func(args)  # 跳转到对应的函数
