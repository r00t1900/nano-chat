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


def current_datetime(format_str: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format_str)


def sub_cmd_bind(arguments):
    # 1 initialize a logger
    log = logger.Logger(config.ROLE_NAME_PAIR + 'SERVER')
    # 2 create a object
    pair_server = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
    # set send and recv timeout to 1s
    pair_server.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, 1000)
    # pair_server.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, 1000)

    # 3 establish a sever to push message
    log.info('binding to {}://{} ...'.format(arguments.protocol, arguments.addr))
    result = pair_server.bind('{}://{}'.format(arguments.protocol, arguments.addr))
    # bind status
    log.info('success') if result else log.info('failed') and exit(0)

    # 4 push loop
    time.sleep(0.5)
    while True:
        content = input('Send({})>'.format(config.COUNT_SEND_SUCCESS))
        # process input message/command
        if content == config.FLAG_SERVER_EXIT:
            # exit command caught, break loop
            log.info(config.L_SERVER_EXIT)
            break
        else:
            try:  # success
                # send message/data/command
                send_result = pair_server.send(bytes(content, encoding=config.DATA_ENCODING))
                config.COUNT_SEND_SUCCESS += 1
            except nnpy.errors.NNError as e:  # failed
                config.COUNT_SEND_FAILED += 1
                log.warning('{}:{}'.format(e, content))

    # 5 close server
    pair_server.close()
    log.info(config.L_SERVER_CLOSED)


def sub_cmd_connect(arguments):
    # 1 initialize a logger
    log = logger.Logger(config.ROLE_NAME_PAIR + 'CLIENT')
    # 2 create a object
    pair_client = nnpy.Socket(nnpy.AF_SP, nnpy.PAIR)
    # set send and recv timeout to 1s
    pair_client.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, 1000)
    # pair_client.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, 1000)
    # keep-alive: not completed yet
    if arguments.keep_alive:
        log.info(config.I_KEEP_ALIVE_ENABLED)
    # 3 connect to a server for receiving message
    log.info('connecting to {}://{}'.format(arguments.protocol, arguments.addr))
    result = pair_client.connect('{}://{}'.format(arguments.protocol, arguments.addr))
    # connect status
    log.info(config.I_OP_SUCCESS) if result else log.info(config.I_OP_FAILED) and exit(0)

    # 4 receive in loop
    time.sleep(0.5)
    while True:
        try:
            recv_data = pair_client.recv()
            if recv_data:
                decoded_data = recv_data.decode(config.DATA_ENCODING)
                # 3 process received data
                # remove the subscribe prefix
                decoded_data = decoded_data[len(arguments.subscribe):]
                # receive a go-offline flag from server, break loop
                if decoded_data == config.FLAG_CLIENT_OFFLINE:
                    log.info(config.L_CLIENT_FLAG_OFFLINE_DETECTED)
                    break
                # display message push by server
                print('{}|{}'.format(current_datetime(), decoded_data))
                # logging to text file
                log.debug(decoded_data)
        except KeyboardInterrupt:
            # ctrl + c detected
            log.info(config.L_CLIENT_CTRL_C)
            break

    # 5 close client
    pair_client.close()
    log.info(config.L_CLIENT_CLOSED)
