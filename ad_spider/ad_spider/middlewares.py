# -*- coding: utf-8 -*-
import random
import urllib

from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver import DesiredCapabilities

from settings import *



class JavaScriptMiddleware(object):

    def __init__(self):
        ip_url = GET_PROXY_URL
        proxy_list = []

        f = urllib.urlopen(ip_url)
        for line in f:
            line = line.strip('\n').strip('\r')
            print "proxy :" + line
            proxy_list.append(line)

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = random.choice(USER_AGENTS)

        service_args = [
            '--proxy=' + random.choice(proxy_list),
            '--proxy-type=http'
        ]

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=service_args)  # 指定使用的浏览器
        print"PhantomJS is starting..."

    def process_request(self, request, spider):

        self.driver.get(request.url)

        content = self.driver.page_source.encode('utf-8')
        #driver.quit()
        return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

    def close_spider(self, spider):
        print "close spider ....."








