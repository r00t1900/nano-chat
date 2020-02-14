# _*_coding:utf-8 _*_
# @Time    : 2020/2/5 9:22
# @Author  : Shek 
# @FileName: logger.py
# @Software: PyCharm
"""
Logging module for local files and console output in the same time.
Have not had time to write description yet since it was used by myself at present time
"""
import logging
import datetime
import os


class Logger:
    def __init__(self, project_name='example', log_folder: str = 'logs', console_level: str = logging.INFO,
                 file_level: str = logging.DEBUG):
        self.arguments = {}
        datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H')
        save_filename = '{} {}.log'.format(project_name, datetime_now)
        save_path = os.path.join(log_folder, save_filename)
        # arguments dict
        logger_arguments = {
            'log_file_path': save_path,
            'level': {'console': console_level, 'file': file_level}
        }

        # arguments hub over here
        self.arguments['logger'] = logger_arguments

        # init and start the logger
        self.__start()

    def __start(self):
        """
        CRITICAL 50|ERROR 40|WARNING 30|INFO 20|DEBUG 10|NOTSET 0
        :return:
        """
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # general configure here
        BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

        # configure console sub-logger here
        console_hlr = logging.StreamHandler()
        console_hlr.setFormatter(formatter)
        console_hlr.setLevel(self.arguments['logger']['level']['console'])

        # configure log-to-file sub-logger here
        file_hlr = logging.FileHandler(self.arguments['logger']['log_file_path'])
        file_hlr.setFormatter(formatter)
        file_hlr.setLevel(self.arguments['logger']['level']['file'])

        # sub-logger handler added here
        self.logger.addHandler(console_hlr)
        self.logger.addHandler(file_hlr)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    def exception(self, msg):
        self.logger.exception(str(msg))
