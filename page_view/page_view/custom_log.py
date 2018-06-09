#coding:utf-8

import os
import datetime
from scrapy import log
import scrapy
from settings import *


class CustomLog:

    @staticmethod
    def log(STATUS = ["ERROR"]):

        for level in STATUS:
            if(CustomLog.__checklevel(level)):
                CustomLog.__run_log(level)
            else:
                CustomLog.__run_log('ERROR')
                scrapy.log.msg("CustomLog.log()ERROR", level=log.ERROR, )

    @staticmethod
    def __run_log(level):

        path = 'log' + os.path.sep + datetime.datetime.now().strftime('%Y-%m-%d') + os.path.sep +  level + os.path.sep

        # 判断日志路径是否存在
        if not os.path.exists(path):
            os.makedirs(path)


        # 启用日志
        scrapy.log.start(logfile=os.getcwd() + os.path.sep +path + datetime.datetime.now().strftime('%H') + '.log', loglevel=level,logstdout=True)


    # 检查日志等级
    @staticmethod
    def __checklevel(level):
        string_lsevl = ['CRITICAL','ERROR','WARNING','INFO','DEBUG']
        if level in string_lsevl:
            return True
        else:
            return False