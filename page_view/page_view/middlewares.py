# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import random
import socket
import urllib
import urllib2
from time import sleep
from selenium.common.exceptions import TimeoutException
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium import webdriver
from settings import *
import scrapy
from scrapy import log
import hashlib
import time

class JavaScriptMiddleware(object):

    def __init__(self,crawler):
        # 初始化代理超时计数
        self.timeout_time = 0
        self.i = 0
        self.create_ua_proxy()
        print"PhantomJS is starting..."

    def process_request(self, request, spider):
        try:
            if self.i < 1:
                self.driver.get(request.url)
                # sleep(random.uniform(0.5, 1))
                sleep(2)
                self.i += 1
            else:
                self.driver.quit()
                self.create_ua_proxy()
                self.driver.get(request.url)
                sleep(2)
                # sleep(random.uniform(0.5, 1))

        except TimeoutException or socket.error,e:
            # print e,e.msg
            print 1
            # print e.__class__
            # print repr(e)
            # if self.timeout_counter():
        content = self.driver.page_source.encode('utf-8')
        return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

    # 生成随机代理和UA
    def create_ua_proxy(self):
        # proxy_list = []
        # self.get_proxy_url = GET_PROXY_URL
        # self.proxy = urllib.urlopen(self.get_proxy_url)
        # self.proxy = ["122.4.41.177:38517"]
        # for line in self.proxy:
        #     line = line.strip('\n').strip('\r')
        #     print "proxy :" + line
        #     proxy_list.append(line)

        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        # ===================new===============================
        _version = sys.version_info
        is_python3 = (_version[0] == 3)

        orderno = "ZF201791967240ZhNTg"
        secret = "e7564fcb9f0741c68a88917d9fdcc896"

        ip = "forward.xdaili.cn"
        port = "80"
        ip_port = ip + ":" + port

        timestamp = str(int(time.time()))  # 计算时间戳
        string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

        if is_python3:
            string = string.encode()

        md5_string = hashlib.md5(string).hexdigest()  # 计算sign
        sign = md5_string.upper()  # 转换成大写
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

        proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
        headers = {"Proxy-Authorization": auth}

        self.service_args = [
            # '--proxy=' + random.choice(proxy_list),
            '--proxy=' + proxy["http"],
            '--proxy-type=http'
        ]

        for key, value in headers.iteritems():
            self.dcap['phantomjs.page.customHeaders.{}'.format(key)] = value

        # ============================end===========================================
        self.dcap["phantomjs.page.settings.userAgent"] = random.choice(USER_AGENTS)

        # 不载入图片，爬页面速度会快很多
        self.dcap["phantomjs.page.settings.loadImages"] = False
        self.service_args.append('--load-images=no')  ##关闭图片加载
        self.service_args.append('--disk-cache=yes')  ##开启缓存
        self.service_args.append('--ignore-ssl-errors=true')  ##忽略https错误

        # 指定使用的浏览器
        if Enable_PROXY:
            # scrapy.log.msg("proxy :" + str(random.choice(proxy_list)), level=log.WARNING)
            # scrapy.log.msg("proxy :" + proxy["http"], level=log.WARNING)
            # scrapy.log.msg("UA :" + self.dcap["phantomjs.page.settings.userAgent"], level=log.WARNING)
            self.driver = webdriver.PhantomJS(service_args=self.service_args,desired_capabilities=self.dcap)
        elif not Enable_PROXY:
            self.driver = webdriver.PhantomJS(desired_capabilities=self.dcap)

        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
        self.driver.set_page_load_timeout(3)
        # sleep(random.uniform(1,1.5))

    # 记录和重置代理超时计数器
    def timeout_counter(self):
        self.timeout_time += 1
        scrapy.log.msg('proxy--timeout1：' + str(self.timeout_time), level=log.WARNING)
        if self.timeout_time < 3:
            return False
        else:
            self.timeout_time = 0
            print '更换代理'
            return True

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    # 结束phantomJS进程
    def spider_closed(self):
        print "spider_closed"
        # self.driver.save_screenshot('moount.png')
        self.driver.quit()








