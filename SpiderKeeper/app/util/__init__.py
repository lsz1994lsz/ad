# -*- coding: utf-8 -*-
import datetime
import requests
import json
import socket


def timedelta(end_time, start_time):
    '''

    :param end_time:
    :param start_time:
    :return:
    '''
    if not end_time or not start_time:
        return ''
    if type(end_time) == str:
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if type(start_time) == str:
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    total_seconds = (end_time - start_time).total_seconds()
    return readable_time(total_seconds)


def readable_time(total_seconds):
    if not total_seconds:
        return '-'
    if total_seconds < 60:
        return '%s s' % total_seconds
    if total_seconds < 3600:
        return '%s m' % int(total_seconds / 60)
    return '%s h %s m' % (int(total_seconds / 3600), int((total_seconds % 3600) / 60))


def project_path():
    import inspect
    import os
    this_file = inspect.getfile(inspect.currentframe())
    return os.path.abspath(os.path.dirname(this_file) + '/../')


from email.header import Header
from email.mime.text import MIMEText
import smtplib

MAIL_HOST = "smtp.exmail.qq.com"  # 发送邮件的smtp服务器
MAIL_USER = "lsz@guruhk.com"      # 发件人邮箱账号
MAIL_PASS = "CmTpG4vH5UtWZYgA"    # 授权码
RECEIVERS = "lsz@guruhk.com"      # 收件人邮箱账号


class EmailSender:

    def __init__(self, mail_host, mail_user, mail_pass, receivers, port=456):
        self.mail_host = mail_host  # 发送邮件的smtp服务器
        self.mail_user = mail_user  # 发件人的用户名/邮箱账号
        self.mail_pass = mail_pass  # 授权码
        self.receivers = receivers  # 收件人邮箱账号
        self.smtp_port = port       # smtp服务器SSL端口号，默认是465

    def send_email(self, job_id, spider_name, error_str):
        # message = MIMEText('job_execution_id is ' + job_id + '\nPS: 出错信息: ' + error_str, 'plain', 'utf-8')  # 邮件内容
        message = MIMEText('job_execution_id is ' + job_id + '\nerror information: ' + error_str, _charset='utf-8')  # 邮件内容
        subject = spider_name + '出错'
        message['Subject'] = Header(subject, 'utf-8')   # 邮件主题
        message['From'] = self.mail_user                # 发件人名 Tim<lsz@guruhk.com>
        message['To'] = self.receivers                  # 收件人名
        try:
            # 发件人邮箱中的SMTP服务器，端口是465
            server = smtplib.SMTP_SSL(self.mail_host, 465)
            # 登录smtp服务器,括号中对应的是发件人邮箱账号、邮箱密码
            login_res = server.login(self.mail_user, self.mail_pass)

            if login_res and login_res[0] == 235:
                # loginRes = (235, b'Authentication successful')
                # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
                server.sendmail(self.mail_user, [self.receivers], message.as_string())
                print "send_success"
            else:
                print "Error: login_fail"
            server.quit()
        except smtplib.SMTPException:
            print "Error: send_fail"
        except Exception as e:
            print e


def specific_error(log):
    '''

    :param log: spider_ending_log(str)
    :return: specific_error_information(list)
    '''
    import re
    pattern = '(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{4} \[.{2,10}\] ERROR: .*?)\d{4}-\d{2}-\d{2}'
    content_list = re.findall(pattern, log, re.S)
    return content_list


def keyword_error(target_error, target_item, spider_name, job_execution_id, error_index):
    # spider_name = 'ipv4'
    # job_execution_id = 3

    spider_name_str = 'error_spider: ' + spider_name
    job_execution_id_str = 'job_execution_id: ' + str(job_execution_id)
    error_info1 = '[ ' + target_error + ' ]' + ' is in log!'
    error_info2 = '[ ' + target_item + ' ]' + ' is not in log!'
    error_info3 = '[ ' + target_error + ' ]' + ' is in log' + ' and ' + '[ ' + target_item + ' ]' + ' is not in log!'
    error_info = [error_info1, error_info2, error_info3]
    content = '\n'.join([spider_name_str, job_execution_id_str, error_info[error_index]])
    return content
    # for i in range(3):
    #     content = '\n'.join([spider_name_str, job_execution_id_str, error_info[i]])
    #     tonews(url_token, content)


def page_info(page_url, page_time, page_title):
    import datetime
    now = datetime.datetime.now()
    now_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    topic = u'刷量完成'
    page_finished = u'完成时间: {}'.format(now_datetime)
    url_info = u'刷量网址: {}'.format(page_url)
    time_info = u'刷量次数: {}'.format(page_time)
    title_info = u'刷量标题: [{}]'.format(page_title)
    content = '\n'.join([topic, page_finished, url_info, time_info, title_info])
    return content



'''
钉钉管理后台 : http://open-dev.dingtalk.com
'''
cron_token = 'a99332b1714bbd716197ee8932846ccc89e4157ca5321b6eb812bbcb75325ef2'
page_token = '40b6a274acb5bd191f4113919b2b3a41c1a76c69f46c6e4123879676e9e3340f'

# 增加test专用钉钉群
if socket.gethostname() in ['55b0b0173dbe', 'DESKTOP-LFMPPIB']:
    cron_token = '37dd5bf1834080c4a4ac2ed1ef37a3df6dd69212201796454ff15c5838f2d531'
    page_token = '589094d8867e9d64331e80e3203044250ca0c0cfb8a6fa07d22f00b33c58b0c6'


# 获取access_token
def access_url(ding_token):
    url = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(ding_token)
    return url


def send_news(url, content):
    '''
    msgtype : 类型
    content : 内容
    '''
    msgtype = 'text'
    values = {
        "msgtype": "text",
        msgtype: {
            "content": content
        },
    }
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    values = json.dumps(values)
    res = requests.post(url, values, headers=headers)
    errmsg = json.loads(res.text)['errmsg']
    if errmsg == 'ok':
        return "ok"
    return "fail: %s" % res.text


def send_error_info(token, content):
    url = access_url(token)
    send_news(url, content)


def get_log(jobexecution):
    from app import agent
    res = requests.get(agent.log_url(jobexecution))
    res.encoding = 'utf8'
    return res.text
