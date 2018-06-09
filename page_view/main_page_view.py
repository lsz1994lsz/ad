import time
import thread
import random
from page_view.settings import *
from subprocess import Popen
from scrapy import cmdline
import sys
import os


# cmdline.execute("scrapy crawl page_view -a url=http://caifuhao.eastmoney.com/news/20171215113353335314930 -a time=21001".split())
cmdline.execute("scrapy crawl page_view -a url=http://caifuhao.eastmoney.com/news/20180516173510351014630 -a time=22000".split())
import sys

# str = sys.argv[1]
# time = sys.argv[2]

# time = 9999
# print "URL is : ", str
# print "TIME is : ", time
# cmdline.execute("scrapy crawl page_view -a url={} -a time={}".format(str,time).split())
# -a -s --set=
import subprocess

# i = 3
# # i = 1000
# while i >= 0:
#     print i
#     Popen("scrapy crawl page_view",shell = True)
#     # sleep_time = random.randint(SLEEP_TIME_MIN, SLEEP_TIME_MAX)
#     # time.sleep(float(sleep_time))
#     time.sleep(35)
#     i = i - 1
# #
# # #
# time.sleep(40)




