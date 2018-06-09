import time
import thread
import random

from subprocess import Popen

import subprocess
from scrapy import cmdline


#i = 500
i = 500
while i >= 0:

	Popen("scrapy crawl ad_spider",shell = True)

	sleep_time = random.randint(10, 15)
	time.sleep(float(sleep_time))
	i = i - 1


time.sleep(50)




