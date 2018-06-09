# -*- coding:utf-8 -*-
import paramiko
from app import db, app
from app import scheduler
from app.spider.model import JobInstance, JobExecution, Project
import datetime
import time
from app.util import *
import random


def enter_server_and_shell(hostname, port, username, password, cmd):
    '''
    inspect server memory
    :return:
    '''
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname=hostname, port=port, username=username, password=password)
    stdin, stdout, stderr = s.exec_command(cmd)
    result = stdout.readlines()

    s.close()

    return result


def enter_server_and_kill(hostname, port, username, password, cmd):
    '''
    inspect server memory
    :return:
    '''
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname=hostname, port=port, username=username, password=password)
    stdin, stdout, stderr = s.exec_command(cmd)
    result = stdout.readlines()
    kill_spider = 'kill -9 {}'.format(int(result[0]))
    s.exec_command(kill_spider)
    s.close()

    return result


def ssh_result(url, total_time):
    '''
    guard server memory
    :return:
    '''
    hostname = '121.40.77.248'
    # hostname = '101.37.29.42'
    port = 22
    username = 'glh-test1'
    password = '0284364'
    cmd = "python ~/gelonghui/gelonghui_pageviews.py {} {}".format(url, total_time)
    result = enter_server_and_shell(hostname, port, username, password, cmd)
    return result


def ssh_kill(url, total_time):
    '''
    guard server memory
    :return:
    '''
    hostname = '121.40.77.248'
    # hostname = '101.37.29.42'
    port = 22
    username = 'glh-test1'
    password = '0284364'
    cmd = "ps aux|grep 'python /home/glh-test1/gelonghui/gelonghui_pageviews.py %s %s'|grep -v grep|awk '{print $2}'" \
          % (url, total_time)
    result = enter_server_and_kill(hostname, port, username, password, cmd)
    return result


def job_instance_get(ge_url, ge_time, ge_title):
    job_instance_ge = JobInstance()
    job_instance_ge.spider_name = 'page_view'
    job_instance_ge.project_id = 1
    job_instance_ge.priority = 0
    job_instance_ge.url = ge_url
    job_instance_ge.time = ge_time
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    job_instance_ge.title = local_time + '_' + ge_title
    job_instance_ge.enabled = -1
    job_instance_ge.mark_ge = 1
    job_instance_ge.run_type = 'onetime'
    job_instance_ge.running_on = 'http://121.40.77.248:6800'
    db.session.add(job_instance_ge)
    db.session.commit()
    return job_instance_ge


def job_execution_get(ge_url, ge_time, job_instance_ge):
    job_execution_ge = JobExecution()
    job_execution_ge.project_id = job_instance_ge.project_id
    job_execution_ge.job_instance_id = job_instance_ge.id
    job_execution_ge.create_time = datetime.datetime.now()
    job_execution_ge.start_time = datetime.datetime.now()
    job_execution_ge.running_on = 'http://121.40.77.248:6800'
    job_execution_ge.service_job_execution_id = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    std_out = ssh_result(ge_url, ge_time)
    return dict(job_execution_ge=job_execution_ge, std_out=std_out)


def judge_stdout(result, job_instance_ge):
    job_execution_ge = result.get('job_execution_ge')
    if 'success\n' in result.get('std_out'):
        app.logger.info('gelonghui successful')
        job_execution_ge.running_status = 2
        job_execution_ge.mark_ge = 1
        job_execution_ge.end_time = datetime.datetime.now()
        job_instance_ge.over_ge = 1
        db.session.add(job_execution_ge)
        db.session.commit()

        # page_gelonghui finished info by dingding
        job_info = job_execution_ge.to_dict()
        job_instance_id = job_info.get('job_instance_id')
        job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
        page_url = job_instance.url
        page_time = job_instance.time
        page_title = job_instance.title
        page_content = page_info(page_url, page_time, page_title)

        # send information by dingding
        send_error_info(page_token, page_content)
    else:
        app.logger.info('gelonghui fail')
        job_execution_ge.running_status = 3
        job_execution_ge.mark_ge = 1
        job_execution_ge.end_time = datetime.datetime.now()
        job_instance_ge.over_ge = 1
        db.session.add(job_execution_ge)
        db.session.commit()


def gelong(ge_url, ge_time, ge_title):
    job_instance_ge = job_instance_get(ge_url, ge_time, ge_title)
    result = job_execution_get(ge_url, ge_time, job_instance_ge)
    judge_stdout(result, job_instance_ge)


def run_cron(job_instance, run_spider_job):
    '''
    add periodic job to scheduler
    :return:
    '''
    running_job_ids = set([job.id for job in scheduler.get_jobs()])
    print 'run cron'
    job_id = "spider_job_%s:%s" % (job_instance.id, int(time.mktime(job_instance.date_created.timetuple())))
    # available_job_ids.add(job_id)
    # print 'available inner', available_job_ids
    if job_id not in running_job_ids:
        try:
            scheduler.add_job(run_spider_job,
                              args=(job_instance.id,),
                              trigger='cron',
                              id=job_id,
                              minute=job_instance.cron_minutes,
                              hour=job_instance.cron_hour,
                              day=job_instance.cron_day_of_month,
                              day_of_week=job_instance.cron_day_of_week,
                              month=job_instance.cron_month,
                              # second=random.randint(0, 59),
                              second=10,
                              # second='*/10',
                              max_instances=999,
                              misfire_grace_time=60 * 60,
                              coalesce=True)
            app.logger.info('[load_spider_job][project:%s][spider_name:%s][job_instance_id:%s][job_id:%s]' % (
                job_instance.project_id, job_instance.spider_name, job_instance.id, job_id))
        except Exception as e:
            app.logger.error(
                '[load_spider_job] failed {} {},may be cron expression format error '.format(job_id, str(e)))


def remove_cron(job_instance):
    running_job_ids = set([job.id for job in scheduler.get_jobs()])
    job_id = "spider_job_%s:%s" % (job_instance.id, int(time.mktime(job_instance.date_created.timetuple())))
    if job_id in running_job_ids:
        try:
            scheduler.remove_job(job_id)
            app.logger.info('[drop_spider_job][job_id:%s]' % job_id)
        except Exception as e:
            app.logger.error(
                '[drop_spider_job] failed [job_id:%s]' % job_id)


def log_cron(cron_job, cron_id):
    scheduler.add_job(cron_job, 'interval', seconds=40, id=cron_id)


def remove_log_cron(cron_id):
    scheduler.remove_job(cron_id)
