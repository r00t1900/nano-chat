# _*_coding:utf-8 _*_
# @Time    : 2020/2/6 11:42
# @Author  : Shek 
# @FileName: func.py
# @Software: PyCharm
import nnpy
import time
import datetime
import config
from module import logger


def current_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def sub_cmd_bind(arguments):
    # initialize a logger
    log = logger.Logger('push')
    # create object
    push_server = nnpy.Socket(nnpy.AF_SP, nnpy.PUSH)
    # 1 establish a sever to push message
    log.info('binding to {}://{} ...'.format(arguments.protocol, arguments.addr))
    result = push_server.bind('{}://{}'.format(arguments.protocol, arguments.addr))
    # bind status
    log.info('success') if result else log.info('failed') and exit(0)

    # 2 push loop
    time.sleep(0.5)
    while True:
        content = input('Send({})>'.format(config.COUNT_SEND_SUCCESS))
        if content == 'exit':
            log.info('closing server...')
            break
        else:
            send_result = push_server.send(bytes(content, encoding='utf-8'))
            if send_result:
                config.COUNT_SEND_SUCCESS += 1
            else:
                config.COUNT_SEND_FAILED += 1
                log.warning('SEND FAILED:{}'.format(content))
    push_server.close()
    log.info('push server closed')


def sub_cmd_connect(arguments):
    # 1 initialize a logger
    log = logger.Logger(config.LOG_NAME_PULL)
    # 2create a object
    pull_client = nnpy.Socket(nnpy.AF_SP, nnpy.PULL)
    # not completed yet
    if arguments.keep_alive:
        print(config.I_KEEP_ALIVE_ENABLED)
    # 3 connect to a server for receiving message
    log.info('connecting to {}://{}'.format(arguments.protocol, arguments.addr))
    result = pull_client.connect('{}://{}'.format(arguments.protocol, arguments.addr))
    # connect status
    log.info(config.I_OP_SUCCESS) if result else log.info(config.I_OP_FAILED) and exit(0)

    # 4 receive in loop
    time.sleep(0.5)
    while True:
        try:
            recv_data = pull_client.recv()
            if recv_data:
                decoded_data = recv_data.decode(config.DATA_ENCODING)
                # 3 process received data
                if decoded_data == config.FLAG_CLIENT_OFFLINE:
                    # receive a go-offline flag from server, break loop
                    log.info(config.L_CLIENT_FLAG_OFFLINE_DETECTED)
                    break
                # display message push by server
                print('{} {}'.format(current_datetime(), decoded_data))
                # logging to text file
                log.debug(decoded_data)
        except KeyboardInterrupt:
            # ctrl + c detected
            log.info(config.L_CLIENT_CTRL_C)
            break

    # 5 close client
    pull_client.close()
    log.info(config.L_CLIENT_CLOSED)
