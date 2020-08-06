# -*- coding:utf-8 -*-
import logging
import logging.handlers
import time
import configparser
import os

class logg():
 
    def __init__(self):
        pass

    @staticmethod
    def logHandler():

        log_dir = 'log'

        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)
        
        # define log output fmt
        fmt_str = '%(asctime)s[level-%(levelname)s][%(name)s]:%(message)s'
        # init basicConfig
        logging.basicConfig()

        fileshandle = logging.handlers.TimedRotatingFileHandler(log_dir + r'\spider.log',
        when='midnight', interval=1, encoding='utf-8')
        
        fileshandle.suffix = "%Y%m%d_%H%M%S.log"
        fileshandle.setLevel(logging.NOTSET)
        formatter = logging.Formatter(fmt_str)
        fileshandle.setFormatter(formatter)

        formatter = logging.Formatter(\
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logger = logging.getLogger('FreeBuf_spider')
        logger.addHandler(fileshandle)
        
        logger.setLevel(logging.INFO)
        return logger

if __name__ == "__main__":
    logHandler = logg.logHandler()
    logHandler.info('test info')
    # config = configparser.ConfigParser()
    # config.read('spider.conf')
    # sec = config.sections()
    # print(sec)
    # print(config['Paths']['logdir'])
    
