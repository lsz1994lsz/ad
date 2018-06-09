# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from scrapy import Selector, Request
from scrapy.contrib.spiders import CrawlSpider





class AdSpider(CrawlSpider):

	name = "ad_spider_post"

	# def start_requests(self):
	# 	start_url_request_list = []
    #
	# 	url = "http://test.gelonghui.com/p/77778.html"
	# 	start_request = Request(url, callback=self.parse)
	# 	start_url_request_list.append(start_request)
    #
	# 	return start_url_request_list

	start_urls = [
		# 'http://test.gelonghui.com/p/77778.html'
		'http://www.gelonghui.com/column/article/146187'
	]

	headers = {
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Accept-Encoding": "gzip, deflate, sdch, br",
		"Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
		"Connection": "keep-alive",
		"Host": "webb-site.com",
		"Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
	}


	def parse(self, response):

		sel = Selector(response)
		href_list = sel.xpath('//*[@id="content"]//div[@class="article-bottom"]/div[@class="footerAd"]//@href')

		for href in href_list:
			# scrapy.log.msg('{0}'.format(href.extract()), level=log.INFO)
			url = href.extract()
			print url
			yield Request(url, callback=self.parse_ad_page,dont_filter=True, headers=self.headers)


	def parse_ad_page(self, response):
		print "-------------------"
		print response.url
		print "-------------------"

