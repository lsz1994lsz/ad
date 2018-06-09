import time
import thread
import random
from ad_spider_post.settings import *
from subprocess import Popen
from scrapy import cmdline
cmdline.execute("scrapy crawl ad_spider_post".split())
import subprocess

# i = 500
# i = 20000
# while i >= 0:
#
#     Popen("scrapy crawl ad_spider_post",shell = True)
#     sleep_time = random.randint(SLEEP_TIME_MIN, SLEEP_TIME_MAX)
#     time.sleep(float(sleep_time))
#     i = i - 1
#
#
# time.sleep(SLEEP_TIME)




