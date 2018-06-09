# -*- coding: utf-8 -*-
import random
import re
import requests
import time

def get():
    view = 0
    while view < 48555:
        try:
            url = 'http://www.gelonghui.com/p/165535.html'
            rep = url.replace('/p/', '/api/post/').replace('.html', '').replace('.htm', '').replace('column/article/','api/columnArticle/getByPostId?postId=')
            txt = requests.get(rep, timeout=1)
            if "www.gelonghui.com" in url:
                view = int(re.findall('read" :(.*?),', txt.content)[0].replace(' ', ''))
            if "m.gelonghui.com" in url:
                view = int(re.findall('<span class="read-count">阅读 (.*?)</span>', txt.content)[0].replace(' ', ''))

        except Exception, e:
            print e
        # time.sleep(random.uniform(0.01, 0.1))
        print view
get()

