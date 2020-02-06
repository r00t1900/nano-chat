# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 18:41
# @Author  : Shek 
# @FileName: OneWayPipe_CLI.py
# @Software: PyCharm
import argparse


def sub_cmd_bind(arguments):
    print('you are attempting to bind {}://{}'.format(arguments.protocol, arguments.addr))


def sub_cmd_connect(arguments):
    print('you are attempting to connect {}://{}'.format(arguments.protocol, arguments.addr))
    if arguments.keep_alive:
        print('automatically reconnect enabled')


parser = argparse.ArgumentParser(
    description='A LAN-chat program written in Python3 http://github.com/YourGithub/RepositoryAddress')
subparsers = parser.add_subparsers()

# command 'bind'
cmd_bind = subparsers.add_parser('bind', help='bind server')
cmd_bind.add_argument('protocol', action='store', nargs='?', default='tcp', help='communicate protocol')
cmd_bind.add_argument('addr', action='store', nargs='?', default='*:4000', help='<host>:<port>')
cmd_bind.set_defaults(func=sub_cmd_bind)

# command 'connect'
cmd_connect = subparsers.add_parser('connect', help='connect to a server')
cmd_connect.add_argument('protocol', action='store', nargs='?', default='tcp', help='communicate protocol')
cmd_connect.add_argument('addr', action='store', nargs='?', default='127.0.0.1:4000', help='<host>:<port>')
cmd_connect.add_argument('--keep-alive', action='store_true', help='automatically reconnect when corrupted')
cmd_connect.set_defaults(func=sub_cmd_connect)

args = parser.parse_args()  # 处理输入的参数
if not hasattr(args, 'func'):
    # 无参数时跳转到-h，否则会提示 namespace object has not attribute 'func'，故这里用hasattr()判断
    args = parser.parse_args(['-h'])
args.func(args)  # 跳转到对应的函数
