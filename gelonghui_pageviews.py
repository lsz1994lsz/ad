import random
import re


import requests
import time

time1 = time.time()
i = 0
while i < 9000:
    txt4 = requests.get('http://www.gelonghui.com/api/post/149231?random=0.14984706231519218')
    i += 1
    print i
    z = re.findall('read" :(.*?),', txt4.content)
    time.sleep(random.uniform(0.01, 0.2))
    print z
print time.time() - time1