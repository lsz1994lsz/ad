# -*- coding: utf-8 -*-
import random
import urllib
from time import sleep

from scrapy.http import HtmlResponse
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import *


class JavaScriptMiddleware(object):

    def __init__(self):
        # ip_url = GET_PROXY_URL
        proxy_list = []

        # f = urllib.urlopen(ip_url)
        # for line in f:
        #     line = line.strip('\n').strip('\r')
        #     print "proxy :" + line
        #     proxy_list.append(line)

        dcap = dict(DesiredCapabilities.PHANTOMJS)

        dcap["phantomjs.page.settings.userAgent"] = random.choice(USER_AGENTS)
        # 不载入图片，爬页面速度会快很多
        # dcap["phantomjs.page.settings.loadImages"] = False


        # service_args = [
        #     '--proxy=' + random.choice(proxy_list),
        #     '--proxy-type=http'
        # ]

        self.driver = webdriver.PhantomJS()  # 指定使用的浏览器
        print"PhantomJS is starting..."

    def process_request(self, request, spider):
        # self.driver = webdriver.PhantomJS()
        # # 画布大小
        # self.driver.set_window_size(1024,1024)

        # 设置20秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
        self.driver.set_page_load_timeout(30)
        # 设置20秒脚本超时时间
        self.driver.set_script_timeout(30)

        self.driver.get(request.url)
        # sleep(1)
        # try:
        # WebDriverWait(self.driver,30, 0.05).until(EC.presence_of_element_located((By.XPATH, "//*[@id='content']//div[@class='article-bottom']/div[@class='footerAd']//*[@href]")))
        # qqq = self.driver.find_elements_by_xpath("//*[@id='content']//div[5]//*[@href]")
        # ActionChains(self.driver).double_click(qqq).perform()
        # self.driver.save_screenshot('csdn.png')
        # finally:
        # for link in self.driver.find_elements_by_xpath("//*[@id='content']//div[@class='article-bottom']/div[@class='footerAd']//*[@href]"):
        #     print (link.get_attribute('href'))
        content = self.driver.page_source.encode('utf-8')
        # 结束phantomJS进程
        # self.driver.quit()

        return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

    def close_spider(self, spider):
        print "close spider ....."








