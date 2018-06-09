import time
import thread
import random
from page_view.settings import *
from subprocess import Popen
from scrapy import cmdline
cmdline.execute("scrapy crawl page_view".split())
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




