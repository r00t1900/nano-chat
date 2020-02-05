# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 8:59
# @Author  : Shek 
# @FileName: config.py
# @Software: PyCharm
data_encoding = 'utf-8'
protocol = 'tcp'
addr_c = '127.0.0.1'  # for client to connect
addr_s = '*'  # for server to bind
port = '4000'
CONNECT_ADDR = '{}://{}:{}'.format(protocol, addr_c, port)
BIND_ADDR = '{}://{}:{}'.format(protocol, addr_s, port)
