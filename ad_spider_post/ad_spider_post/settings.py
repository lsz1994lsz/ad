# -*- coding: utf-8 -*-

# Scrapy settings for ad_spider_post project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
# from ad_spider.custom_log import CustomLog

# ==============日志相关=================
# 自定义的日志，默认为ERROR，可用级别为：CRITICAL，ERROR，WARNING，INFO，DEBUG
# CustomLog.log(['ERROR','INFO'])
# 全局日志开关
# LOG_ENABLED = True
# 日志编码
# LOG_ENCODING = 'utf-8'
# 定义日志级别
# LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'WARNING'
# LOG_LEVEL = 'ERROR'
# 定义日志路径
# LOG_FILE = r'D:\ceshi\s.log'
# 记录Scrapy中的标准输出
# LOG_STDOUT = False
BOT_NAME = 'ad_spider_post'

SPIDER_MODULES = ['ad_spider_post.spiders']
NEWSPIDER_MODULE = 'ad_spider_post.spiders'


#取消默认的useragent,使用新的useragent
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None ,#关闭默认下载器
    'ad_spider_post.middlewares.JavaScriptMiddleware':500, #键为中间件类的路径，值为中间件的顺序
}

USER_AGENTS = [
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
	"Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
	"Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
	"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
	"Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
	"Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
	"Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
	"Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
	"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
	"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.1",
	"Opera/9.80 (Windows NT 6.1; U; en)Presto/2.8.131 Version/11.11",
	"Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
	"Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; NexusOne Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 MobileSafari/533.1",
	"MQQBrowser/26 Mozilla/5.0 (Linux; U;Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1(KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
]
#
GET_PROXY_URL = "http://www.xdaili.cn/ipagent/greatRecharge/getGreatIp?spiderId=fa88b90f2a194d7cbd76b89795a2ee66&orderno=YZ2017815605yJ6Xxz&returnType=1&count=1"
#
ROBOTSTXT_OBEY = False


SLEEP_TIME_MIN = 10
SLEEP_TIME_MAX = 15
SLEEP_TIME = 20
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ad_spider_post (+http://www.yourdomain.com)'
