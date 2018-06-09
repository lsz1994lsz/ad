# -*- coding: UTF-8 -*-
import random

from ..settings import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
from datetime import datetime

from scrapy import Selector, Request
from scrapy.contrib.spiders import CrawlSpider
import scrapy
from scrapy import log


class PageViewSpider(CrawlSpider):
    name = "page_view"

    # start_urls = [
    #     # 'http://test.gelonghui.com/p/77778.html'
    # ]

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Host": "webb-site.com",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
    }

    # URL
    def start_requests(self):
        start_url_request_list = []
        i = 1
        while i <= RUN_TIME:
            # url = "http://caifuhao.eastmoney.com/news/20170912112857285721120"
            url = URL
            # url = "http://emcreative.eastmoney.com/Fortune/V/Share_ArticleDetail/20170906161530153028120"
            # url = "http://127.0.0.1:2017/p/87673.html"
            start_request = Request(url, callback=self.parse,dont_filter=True)#,headers={'Referer': 'http://www.example.com/'})
            start_url_request_list.append(start_request)
            i += 1
        return start_url_request_list


    def parse(self, response):
        sel = Selector(response)
        time.sleep(random.uniform(0.5, 1))
        print response.url
        # print response.body

        # 财富
        readcount = sel.xpath('//*[@id="readcount"]/text()')
        for i in readcount:
            print i.extract()
            # scrapy.log.msg(str(i.extract()), level=log.WARNING)

        # 中金
        # readcount2 = sel.xpath('//html/body/div[3]/div[1]/div[3]/div/div[1]/text()')
        # print readcount2[3].extract()

        # 格隆汇
        # readcount2 = sel.xpath('//*[@id="content"]/div/div/div[1]/div[1]/div[2]/p[2]/span[1]/em[1]/text()')
        # print readcount2[0].extract()

        # yield Request(url=response.url,callback=self.parse,dont_filter=True)
        # yield Request(url, dont_filter=True, headers=self.headers)