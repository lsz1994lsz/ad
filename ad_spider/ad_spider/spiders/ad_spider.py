from scrapy import Selector, Request
from scrapy.contrib.spiders import CrawlSpider

class AdSpider(CrawlSpider):
	name = "ad_spider"

	start_urls = [
		"http://test.gelonghui.com/?abc=spider_lin"
		#"http://116.62.109.1"
		#"http://172.18.15.253:8080/?abcccc=aerknc"
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

		print response.body

		sel = Selector(response)

		li_list = sel.xpath('//ul[@class="ads"]//li')

		for li in li_list:
			#li = li_list[0]
			href = li.xpath(".//a//@href").extract()[0] + "&ab=1234890"
			yield Request(href, callback=self.parse_guru_ad_page,dont_filter=True, headers=self.headers)








	def parse_guru_ad_page(self,response):

		href = response.url
		index = href.find(u"adlink=")
		href2 = href[index+7:]

		and_index = href2.find("&")

		url = ""

		if and_index == -1:
			url = href2
		else:
			url = href2[:and_index]

		print url

		if url != "":
			yield Request(url, callback=self.parse_ad_page, dont_filter=True, headers=self.headers)


	def parse_ad_page(self, response):

		print "-------------------"
		#print response.body
