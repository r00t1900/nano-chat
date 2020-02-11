# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 8:59
# @Author  : Shek 
# @FileName: config.py
# @Software: PyCharm

# universal configuration
DATA_ENCODING = 'utf-8'
PROTOCOL = 'tcp'
HOST_BIND = '*'
HOST_CONNECT = '127.0.0.1'
PORT = '4000'
CONNECT_ADDR = '{}:{}'.format(HOST_CONNECT, PORT)
BIND_ADDR = '{}:{}'.format(HOST_BIND, PORT)
CONNECT_SUBSCRIBE = ''
# program configuration
NN_MODE = 'PAIR MODE'
PROGRAM_URL = 'http://github.com/YourGithub/RepositoryAddress'
PROGRAM_DESCRIPTION = 'A {} LAN-chat program written in Python3 {}'.format(NN_MODE, PROGRAM_URL)
ROLE_NAME_PUSH = 'push'
ROLE_NAME_PULL = 'pull'
ROLE_NAME_PUB = 'pub'
ROLE_NAME_SUB = 'sub'
ROLE_NAME_PAIR = 'pair'
# info text
I_OP_SUCCESS = 'success'
I_OP_FAILED = 'failed'
I_KEEP_ALIVE_ENABLED = 'automatically reconnect enabled'

I_SUBSCRIBE_ALL = 'configured to receive all message'
I_SUBSCRIBE_SPECIFIC_PREFIX = 'configured to receive message start with:'
# help text
H_BIND = 'bind server'
H_BIND_PROTOCOL = 'communicate protocol'
H_BIND_ADDR = '<host>:<port>'
H_CONNECT = 'connect to a server'
H_CONNECT_PROTOCOL = 'communicate protocol'
H_CONNECT_ADDR = '<host>:<port>'
H_CONNECT_KEEP_ALIVE = 'automatically reconnect when corrupted'
H_CONNECT_SUBSCRIBE = 'subscribe the message that you are interested in'
# OneWayPipe DEFAULT CONFIGURATION
# count
COUNT_SEND_SUCCESS = 0
COUNT_SEND_FAILED = 0
# flag
FLAG_CLIENT_OFFLINE = 'client-offline-now'
FLAG_SERVER_EXIT = 'server-exit-now'
# log text
L_CLIENT_CTRL_C = 'closing...'
L_CLIENT_FLAG_OFFLINE_DETECTED = 'offline flag received from server, closing...'
L_CLIENT_CLOSED = 'client closed'

L_SERVER_EXIT = 'closing...'
L_SERVER_CLOSED = 'server closed'
L_SERVER_SEND_FAILED_PREFIX = 'SEND FAILED'
