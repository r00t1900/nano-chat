# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 8:55
# @Author  : Shek 
# @FileName: pull.py
# @Software: PyCharm
import nnpy
import time
import config
from module import logger

logger = logger.Logger('PULL')
pull = nnpy.Socket(nnpy.AF_SP, nnpy.PULL)
pull.connect(config.CONNECT_ADDR)

logger.info('PULL client is started')

while True:
    try:
        recv_data = pull.recv()
        if recv_data:
            logger.info('RECV|{}'.format(recv_data.decode(config.data_encoding)))
        else:
            logger.warning('RECV|EMPTY')
    except Exception as e:
        print(e)
        break
    time.sleep(1)

pull.close()

logger.info('Client \'pull\' is stopped')
