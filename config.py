# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 8:59
# @Author  : Shek 
# @FileName: config.py
# @Software: PyCharm

# universal CONFIGURATION
DATA_ENCODING = 'utf-8'
PROTOCOL = 'tcp'
HOST_BIND = '*'
HOST_CONNECT = '127.0.0.1'
PORT = '4000'
CONNECT_ADDR = '{}:{}'.format(HOST_CONNECT, PORT)
BIND_ADDR = '{}:{}'.format(HOST_BIND, PORT)

# OneWayPipe DEFAULT CONFIGURATION
SEND_SUCCESS = 0
SEND_FAILED = 0
CLIENT_OFFLINE_FLAG = 'go-offline-now'
LOG_TEXT = {
    'client_closed': 'pull client closed',
    'client_ctrl_c': 'closing...',
    'client_offline_flag_detected': 'offline flag receive from server, closing...',
}
