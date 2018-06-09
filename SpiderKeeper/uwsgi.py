#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time      : 2017-09-24 14:53
# @Author    : modm
'''
you can start the server by uwsgi
like gunicorn -w 4 SpiderKeeper.uwsgi:app
'''

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 2017-8-20 钉钉API发送消息

# import requests
# import json
# import os
# import sys
#
# '''
# 钉钉管理后台 : http://open-dev.dingtalk.com
# '''
# access_token = 'a99332b1714bbd716197ee8932846ccc89e4157ca5321b6eb812bbcb75325ef2'
#
#
# # 获取access_token
# def getToken():
#     url_token = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(access_token)
#     return url_token
#
#
# # url 网站 content 发送的内容
# def tonews(url, content):
#     '''
#     msgtype : 类型
#     content : 内容
#     '''
#     msgtype = 'text'
#     values = {
#         "msgtype": "text",
#         msgtype: {
#             "content": content
#         },
#     }
#     headers = {"Content-Type": "application/json; charset=UTF-8"}
#     values = json.dumps(values)
#     res = requests.post(url, values, headers=headers)
#     errmsg = json.loads(res.text)['errmsg']
#     if errmsg == 'ok':
#         return "ok"
#     return "fail: %s" % res.text
#
#
# # if __name__ == '__main__':
# #     url_token = getToken()
# #     content = '\n'.join(sys.argv[2:])
# #     if not content:
# #         content = '111'
# #     print tonews(url_token, content)
#
# url_token = getToken()
#
# target_error = 'log_count/ERROR'
# target_item = 'item_scraped_count'
#
# spider_name = 'ipv4'
# job_execution_id = 3
#
# spider_name_str = 'error_spider: ' + spider_name
# job_execution_id_str = 'job_execution_id: ' + str(job_execution_id)
# error_info1 = '[ ' + target_error + ' ]' + ' is in log!'
# error_info2 = '[ ' + target_item + ' ]' + ' is not in log!'
# error_info3 = '[ ' + target_error + ' ]' + ' is in log' + ' and ' + '[ ' + target_item + ' ]' + ' is not in log!'
# error_info = [error_info1, error_info2, error_info3]
# for i in range(3):
#     content = '\n'.join([spider_name_str, job_execution_id_str, error_info[i]])
#     tonews(url_token, content)
