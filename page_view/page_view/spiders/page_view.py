# -*- coding: UTF-8 -*-
import random

from scrapy.exceptions import CloseSpider

from ..settings import *
import sys
reload(sys)

sys.setdefaultencoding('utf8')
import scrapy
from scrapy import log
import time
from scrapy import Selector, Request
from scrapy.contrib.spiders import CrawlSpider
from custom_log_v2 import CustomLog


class PageViewSpider(CrawlSpider):
    # CustomLog(CUSTOM_LOG_LEVEL)
    name = "page_view"
    # print name


    def __init__(self, url=None, time=None, ENABLE_PROXY=None, *args, **kwargs):
        self.i = 0
        self.URL = url
        self.RUN_TIME = time
        self.ENABLE_PROXY = ENABLE_PROXY
        # print self.URL
        # print self.RUN_TIME
        # from scrapy.conf import settings
        # print settings.get('ENABLE_PROXY')
        # print 1111111

        # settings = {
        #     'ENABLE_PROXY': 'zzzzzzzzzzzz',
        # }
        # print settings.get('ENABLE_PROXY')
        #
        # from scrapy.conf import settings
        # settings.set('ENABLE_PROXY', 'aaaaaaaaaaaaaa')
        # print settings.get('ENABLE_PROXY')
        #
        #
        # from scrapy.settings import Settings
        # settings = Settings()
        # settings.set('ENABLE_PROXY', 'firefox')
        # print settings.get('ENABLE_PROXY')
        #
        # from scrapy.utils.project import get_project_settings
        # settings = get_project_settings()
        # settings.set('ENABLE_PROXY', 'firefoxzzzzzzzzzz')
        # print settings.get('ENABLE_PROXY')
    #
    # headers = {
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    #     "Accept-Encoding": "gzip, deflate, sdch, br",
    #     "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
    #     "Connection": "keep-alive",
    #     "Host": "webb-site.com",
    #     "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
    # }

    # URL
    def start_requests(self):
        start_url_request_list = []
        i = 1

        while i <= int(self.RUN_TIME)*1.5:
            url = self.URL

            start_request = Request(url, callback=self.parse,dont_filter=True)#,headers={'Referer': 'http://www.example.com/'}),headers = self.headers不断开和关
            start_url_request_list.append(start_request)
            i += 1
        scrapy.log.msg("预计刷 :" + str(self.RUN_TIME), level=log.WARNING)
        return start_url_request_list


    def parse(self, response):
        sel = Selector(response)
        print response.url
        print response.status
        # print response.body
        self.i += 1

        if int(self.i) > int(self.RUN_TIME):
            raise CloseSpider('完成  ' + str(self.i) + '  ' + response.url)
        # 财富
        # if "caifuhao.eastmoney.com" in response.url:
        #     readcount = sel.xpath('//*[@id="readcount"]/text()')
        #     self.judge_pv(readcount, response.url)
        # # 财富移动版
        # if "emcreative.eastmoney.com" in response.url:
        #     readcount = sel.xpath('//html/body/div[2]/div[2]/p/text()')
        #     self.judge_pv(readcount, response.url)
        # # 中金
        # elif "mp.cnfol.com" in response.url:
        #     readcount = sel.xpath('//html/body/div[3]/div[1]/div[3]/div/div[1]/span[2]/text()')
        #     self.judge_pv(readcount ,response.url)
        # # 格隆汇网页
        # elif "www.gelonghui.com" in response.url:
        #     readcount = sel.xpath('//*[@id="content"]/div/div/div[1]/div[1]/div[2]/p[2]/span[1]/em[1]/text()')
        #     self.judge_pv(readcount, response.url)
        # # 格隆汇移动版
        # elif "m.gelonghui.com" in response.url:
        #     readcount = sel.xpath('/html/body/section/div[1]/div[1]/span/text()')
        #     self.judge_pv(readcount, response.url)
        # # 格隆汇column/article/
        # elif "www.gelonghui.com" in response.url:
        #     readcount = sel.xpath('//*[@id="main"]/div[2]/div[1]/span[2]/text()')
        #     self.judge_pv(readcount, response.url)
        # # 搜狐
        # elif "www.sohu.com" in response.url:
        #     readcount = sel.xpath('//*[@id="article-container"]/div[2]/div[1]/div[3]/div[1]/span/em/text()')
        #     self.judge_pv(readcount, response.url)
        # # 搜狐移动版
        # elif "m.sohu.com" in response.url:
        #     readcount = sel.xpath('//html/body/div[3]/div[3]/article/div/span/em/text()')
        #     self.judge_pv(readcount, response.url)

        # yield Request(url=response.url,callback=self.parse,dont_filter=True)
        # yield Request(url, dont_filter=True, headers=self.headers)


    def judge_pv(self,readcount,url):

        if not readcount == []:
            i = readcount[0].extract()
            i = str(i).replace('阅读 ', '').replace(u'阅读：','')
            if "万" in i:
                views = str(i).replace('万', '')
                run_time = float(self.RUN_TIME) / 10000
                scrapy.log.msg(views + "万 :预计刷" + str(run_time) + "万" , level=log.WARNING)
                if float(views) >= run_time:
                    raise CloseSpider(views + '万 完成')
            elif int(i) == 0:
                raise Exception("PV==0")
            else:
                # print i, self.RUN_TIME
                scrapy.log.msg(i + " :" + str(self.RUN_TIME), level=log.WARNING)
                if int(i) > int(self.RUN_TIME):
                    raise CloseSpider( '完成  ' + str(i) +  '  ' + url )

        else:
            self.i += 1
            scrapy.log.msg(" PV==None次数:" + str(self.i), level=log.WARNING)
            if self.i > 2:
                self.i = 0
                raise Exception("PV==None")

