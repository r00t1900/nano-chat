# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 8:52
# @Author  : Shek 
# @FileName: push.py
# @Software: PyCharm
import nnpy
import time
import config
from module import logger

logger = logger.Logger('PUSH')
push = nnpy.Socket(nnpy.AF_SP, nnpy.PUSH)
push.bind(config.BIND_ADDR)

logger.info('PUSH server is started')

for i in range(1, 10 + 1):
    data = 'PUSH|task ID={}'.format(i)
    push.send(bytes(data, encoding=config.data_encoding))
    logger.info('SENT|{}'.format(data))
    time.sleep(1)

push.close()

logger.info('Server \'push\' is stopped')
