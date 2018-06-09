# coding=utf8
import threading
import paramiko
import requests
import time
import config
from app.util import *
from app import scheduler, app, agent, db
from app.spider.model import Project, JobInstance, SpiderInstance, CronJobInstance, JobExecution

# import alive   #  PYTHONPATH/alive.py, 记录scrapyd的状态
# import sys
error_email = EmailSender(MAIL_HOST, MAIL_USER, MAIL_PASS, RECEIVERS)


def sync_job_execution_status_job():
    '''
    sync job execution running status
    :return:
    '''
    print 'sync_job_execution_status_job start'
    for project in Project.find_all_project():
        agent.sync_job_status(project)
    app.logger.debug('[sync_job_execution_status]')


# def sync_spiders():
#     '''
#     sync spiders
#     :return:
#     '''
#     servers = config.SERVERS
#     for index in range(len(servers)):
#         for project in Project.query.all():
#             spider_instance_list = agent.get_spider_list(project, index)
#             # print 'spider_instance_list: {}'.format(spider_instance_list)
#             SpiderInstance.update_spider_instances(project.id, spider_instance_list)
#         app.logger.debug('[sync_spiders]')


def run_spider_job(job_instance_id):
    '''
    run spider by scheduler
    :param job_instance_id:
    :return:
    '''
    try:
        job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
        if job_instance is None:
            content = 'Query fail --> Cannot query the one which id == {} in sk_job_instance'.format(job_instance_id)
            send_error_info(cron_token, content)
        if not job_instance:
            print 'no such job_instance of job_instance_id {}'.format(job_instance_id)
        agent.start_spider(job_instance)
        app.logger.info('[run_spider_job][project:%s][spider_name:%s][job_instance_id:%s]' % (
            job_instance.project_id, job_instance.spider_name, job_instance.id))
    except Exception as e:
        app.logger.error('[run_spider_job] ' + str(e))


# available_job_ids = set()
def sync_cron():
    print 'sync cron'
    running_job_ids = set([job.id for job in scheduler.get_jobs()])
    for cron_instance in CronJobInstance.query.filter_by(enabled=0, run_type="periodic").all():
        print 'cron_instance id is {}, cron_instance enable is {}'.format(cron_instance.id, cron_instance.enabled)
        job_instance = JobInstance.find_job_instance_by_id_common(cron_instance.job_id)
        if job_instance is None:
            content = 'Query fail --> Cannot query the one which id == {} in sk_job_instance'.format(cron_instance.job_id)
            send_error_info(cron_token, content)
        job_id = "spider_job_%s:%s" % (job_instance.id, int(time.mktime(job_instance.date_created.timetuple())))
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


def get_log(jobexecution, job_instance_id_inner):
    job_execution_cron = jobexecution.find_job_of_not_read_over(job_instance_id_inner)
    if not job_execution_cron:
        return
    target_error = 'log_count/ERROR'
    target_item = 'item_scraped_count'
    res = requests.get(agent.log_url(job_execution_cron))
    res.encoding = 'utf8'
    log = res.text

    def error_action(error_info):
        job_execution_cron.read_over = 1
        db.session.commit()
        app.logger.info('Job_execution is read over.')
        job_instance_id = job_execution_cron.job_instance_id
        job_instance_cron = JobInstance.find_job_instance_by_id_common(job_instance_id)
        spider_name = job_instance_cron.spider_name

        error_email.send_email(str(job_instance_cron.id), spider_name, error_info)

    print 'log'
    if target_error in log and target_item not in log:
        error_str = '[ ' + target_error + ' ]' + ' and ' + '[ ' + target_item + ' ]'
        error_action(error_str)
    elif target_error in log:
        error_str = '[ ' + target_error + ' ]'
        error_action(error_str)
    elif target_item not in log:
        error_str = '[ ' + target_item + ' ]'
        error_action(error_str)
    else:
        if job_execution_cron.running_status in [2, 3]:
            job_execution_cron.read_over = 1
            db.session.commit()
            print 'read_over=1 job_execution id is {}'.format(job_execution_cron.id)
    return 'log over'


def schedule_log_cron():
    pass
    # print 'schedule_log_cron'
    # running_job_ids = set([job.id for job in scheduler.get_jobs()])
    # # for project in Project.query.filter(Project.id != 1).all():
    # for job_instance in JobInstance.query.filter(JobInstance.is_deleted == 0,
    #                                              JobInstance.project_id != 1, JobInstance.enabled == 0).all():
    #     # job_id = 'project: {}'.format(project.project_name)
    #     job_id = "spider_log_%s:%s" % (job_instance.id, int(time.mktime(job_instance.date_created.timetuple())))
    #     if job_id not in running_job_ids:
    #         try:
    #             scheduler.add_job(get_log,
    #                               args=(JobExecution, job_instance.id),
    #                               trigger='cron',
    #                               id=job_id,
    #                               minute=30,
    #                               hour="*",
    #                               day="*",
    #                               day_of_week="*",
    #                               month="*",
    #                               second=0,
    #                               max_instances=999,
    #                               misfire_grace_time=60 * 60,
    #                               coalesce=True)
    #             app.logger.info('[load_log_cron][job_instance_id:{}]'.format(job_instance.id))
    #         except Exception as e:
    #             app.logger.error(
    #                 '[load_log_cron] failed {}'.format(str(e)))


# def reload_runnable_spider_job_execution():
#     '''
#     add periodic job to scheduler
#     :return:
#     '''
#     print 'schedule cron spider'
#     running_job_ids = set([job.id for job in scheduler.get_jobs()])
#     # app.logger.debug('[running_job_ids] %s' % ','.join(running_job_ids))
#     available_job_ids = set()
#     # global available_job_ids
#     # add new job to schedule
#     # a = JobInstance.query.filter_by(enabled=0, run_type=u"periodic").all()
#     # print len(a)
#     for job_instance in JobInstance.query.filter_by(enabled=0, run_type="periodic").all():
#         # print 'job instance', job_instance
#         job_id = "spider_job_%s:%s" % (job_instance.id, int(time.mktime(job_instance.date_modified.timetuple())))
#         available_job_ids.add(job_id)
#         print 'available inner', available_job_ids
#         if job_id not in running_job_ids:
#             try:
#                 scheduler.add_job(run_spider_job,
#                                   args=(job_instance.id,),
#                                   trigger='cron',
#                                   id=job_id,
#                                   minute=job_instance.cron_minutes,
#                                   hour=job_instance.cron_hour,
#                                   day=job_instance.cron_day_of_month,
#                                   day_of_week=job_instance.cron_day_of_week,
#                                   month=job_instance.cron_month,
#                                   second=0,
#                                   max_instances=999,
#                                   misfire_grace_time=60 * 60,
#                                   coalesce=True)
#             except Exception as e:
#                 app.logger.error(
#                     '[load_spider_job] failed {} {},may be cron expression format error '.format(job_id, str(e)))
#             app.logger.info('[load_spider_job][project:%s][spider_name:%s][job_instance_id:%s][job_id:%s]' % (
#                 job_instance.project_id, job_instance.spider_name, job_instance.id, job_id))
#
#     # remove invalid jobs
#     for invalid_job_id in filter(lambda job_id: job_id.startswith("spider_job_"),
#                                  running_job_ids.difference(available_job_ids)):
#         scheduler.remove_job(invalid_job_id)
#         app.logger.info('[drop_spider_job][job_id:%s]' % invalid_job_id)
#
#     print 'running job id', running_job_ids
#     print 'available job id', available_job_ids

# def inspect_scrapyd_alive():
#     import requests
#
#     # url = 'http://121.40.77.248:6800/'
#     url = 'http://localhost:6800'
#     try:
#         requests.get(url, timeout=3)
#         # requests.get(url, timeout=1)
#         # print r.status_code
#     except:
#         local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#         app.logger.error('[scrapyd die] in [{}]'.format(local_time))
#         result = JobExecution.list_all_executions()
#         all_pending = result.get('PENDING')
#         all_running = result.get('RUNNING')
#         if all_pending:
#             for pending in all_pending:
#                 if pending.scrapyd_alive == 1:
#                     pending.scrapyd_alive = 0
#                     job_instance_id = pending.job_instance_id
#                     job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
#                     job_instance.scrapyd_alive = 0
#                     db.session.add(job_instance)
#                     db.session.add(pending)
#                     db.session.commit()
#         if all_running:
#             for running in all_running:
#                 if running.scrapyd_alive == 1:
#                     running.scrapyd_alive = 0
#                     job_instance_id = running.job_instance_id
#                     job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
#                     job_instance.scrapyd_alive = 0
#                     db.session.add(job_instance)
#                     db.session.add(running)
#                     db.session.commit()


# def cancel_error_executions():
#     # print 'cancel error'
#     result = JobExecution.list_all_scrapyd_die_executions()
#     pending = result.get('PENDING')
#     running = result.get('RUNNING')
#     if pending:
#         print 'cancel pending'
#         print 'len pending', len(pending)
#         for job_execution in pending:
#             agent.cancel_spider(job_execution)
#     if running:
#         print 'cancel running'
#         print 'len running', len(running)
#         for job_execution in pending:
#             agent.cancel_spider(job_execution)

# scrapyd意外end时,记录spider,scrapyd重启时可以删除invalid jobs, 并重启之

# def inspect_scrapyd_status():
#     reload(alive)
#     return dict(alive=alive.ALIVE, death=alive.DEATH)
#
#
# def mark_error_executions():
#     # 数据库标记此刻的pending以及running
#     local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#     app.logger.error('[scrapyd die] in [{}]'.format(local_time))
#     result = JobExecution.list_all_executions()
#     all_pending = result.get('PENDING')
#     all_running = result.get('RUNNING')
#     if all_pending:
#         for pending in all_pending:
#             if pending.scrapyd_alive == 1:
#                 pending.scrapyd_alive = 0
#                 job_instance_id = pending.job_instance_id
#                 job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
#                 job_instance.scrapyd_alive = 0
#                 db.session.commit()
#     if all_running:
#         for running in all_running:
#             if running.scrapyd_alive == 1:
#                 running.scrapyd_alive = 0
#                 job_instance_id = running.job_instance_id
#                 job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
#                 job_instance.scrapyd_alive = 0
#                 db.session.commit()
#     if 'win' in sys.platform:
#         with open(r'D:/python/spider-test/public/alive.py', 'a') as f:
#             f.write('DEATH = "1"\n')
#     else:
#         with open(r'/home/dev003/pythonpath/alive.py', 'a') as f:
#             f.write('DEATH = "1"\n')
#
#
# def cancel_error_executions():
#     # 剔除数据库标记此刻的pending以及running
#     # print 'cancel error'
#     result = JobExecution.list_all_scrapyd_die_executions()
#     pending = result.get('PENDING')
#     running = result.get('RUNNING')
#     if pending:
#         print 'cancel pending'
#         print 'len of pending', len(pending)
#         for job_execution in pending:
#             agent.cancel_spider(job_execution)
#     if running:
#         print 'cancel running'
#         print 'len of running', len(running)
#         for job_execution in running:
#             agent.cancel_spider(job_execution)
#
#
# def reload_error_executions():
#     # 重启剔除的jobs
#     result = JobInstance.list_all_scrapyd_die_job_instances()
#     if result:
#         for job_instance in result:
#             agent.start_spider(job_instance)
#             job_instance.scrapyd_alive = 1
#             db.session.commit()
#     if 'win' in sys.platform:
#         with open(r'D:/python/spider-test/public/alive.py', 'a') as f:
#             f.write('ALIVE = "1"\n')
#     else:
#         with open(r'/home/dev003/pythonpath/alive.py', 'a') as f:
#             f.write('ALIVE = "1"\n')
#
#
# def supervise_scrapyd():
#     alive_dict = inspect_scrapyd_status()
#     alive_status = alive_dict.get('alive')
#     death_statue = alive_dict.get('death')
#     if death_statue == 1:
#         mark_error_executions()
#     if alive_status == 1:
#         cancel_error_executions()
#         reload_error_executions()

# END

# def inspect_server_memory(hostname, port, username, password, cmd):
#     '''
#     inspect server memory
#     :return:
#     '''
#     s = paramiko.SSHClient()
#     s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     s.connect(hostname=hostname, port=port, username=username, password=password)
#     stdin, stdout, stderr = s.exec_command(cmd)
#     result = stdout.readlines()
#     # stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.
#     available = int(result[1].split()[-1])
#     total = int(result[1].split()[1])
#     s.close()
#
#     return dict(total=total, available=available)
#
#
# def guard_server_memory():
#     '''
#     guard server memory
#     :return:
#     '''
#     # hostname = '121.40.77.248'
#     hostname = '101.37.29.42'
#     port = 22
#     username = 'glh-test1'
#     password = '0284364'
#     cmd = "free -m"
#
#     local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#     inspect_memory = inspect_server_memory(hostname, port, username, password, cmd)
#     available = inspect_memory.get('available')
#     total = inspect_memory.get('total')
#     percent = '{:.2%}'.format(.1 * available / total)
#     limit_mem = 300
#     with open('server_mem.txt', 'ab') as f:
#         print >> f, 'local_time: {}, available: {}, total: {}, percent: {}'.format(local_time, available,
#                                                                                    total, percent)
#     if available < limit_mem:
#         # project_name = u'page_view'
#         project_name = u'刷量'
#         project_id = Project.find_project_id_by_name(project_name)
#         job_execution = JobExecution.find_first_running_job(project_id)
#         if job_execution:
#             job_instance_id = job_execution.job_instance_id
#             job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
#             agent.cancel_spider(job_execution)
#             job_execution.occur_error = 1
#             db.session.add(job_execution)
#             db.session.commit()
#             error_executions = JobInstance.detail_of_error_executions()
#             print 'error of executions', error_executions
#             with open('server_mem.txt', 'ab') as f:
#                 # print >> f, 'It is dangerous, available Memory(M) at {}: {}'.format(local_time, available)
#                 str_info = '[local_time]: {}, [available]: {}, [time]: {}, [title]: {}, [url]: {}'
#                 print >> f, str_info.format(str(local_time), str(available), str(job_instance.time),
#                                             job_instance.title.encode('utf8'),
#                                             job_instance.url.encode('utf8'))
#
#
# def inspect_docker_memory(hostname, port, username, password, cmd):
#     '''
#     inspect server memory
#     :return:
#     '''
#     s = paramiko.SSHClient()
#     s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     s.connect(hostname=hostname, port=port, username=username, password=password)
#
#     stdin, stdout, stderr = s.exec_command(cmd)
#     # stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.
#     # available = int(stdout.readlines()[1].split()[-1])
#     usage = float(stdout.readlines()[-1].split()[3][:-3])
#     # print 'return', type(usage), usage
#     s.close()
#
#     return usage
#
#
# def guard_docker_memory():
#     '''
#     guard server memory
#     :return:
#     '''
#     # hostname = '121.40.77.248'
#     hostname = '101.37.29.42'
#     port = 22
#     username = 'glh-test1'
#     password = '0284364'
#     cmd = "cat /home/dev003/3.txt"
#
#     local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#     usage = inspect_docker_memory(hostname, port, username, password, cmd)
#     total = 1.465 * 1024
#     available = total - usage
#     limit_mem = 300
#     print 'available', type(available), available
#     if available < limit_mem:
#         # project_name = u'page_view'
#         project_name = u'刷量'
#         project_id = Project.find_project_id_by_name(project_name)
#         job_execution = JobExecution.find_first_running_job(project_id)
#         job_execution.occur_error = 1
#         db.session.add(job_execution)
#         db.session.commit()
#         if job_execution:
#             job_instance_id = job_execution.job_instance_id
#             job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
#             agent.cancel_spider(job_execution)
#             job_execution.occur_error = 1
#             db.session.add(job_execution)
#             db.session.commit()
#             error_executions = JobInstance.detail_of_error_executions()
#             print 'error of executions', error_executions
#             with open('server_mem.txt', 'ab') as f:
#                 # print >> f, 'It is dangerous, available Memory(M) at {}: {}'.format(local_time, available)
#                 str_info = '[local_time]: {}, [available]: {}, [time]: {}, [title]: {}, [url]: {}'
#                 print >> f, str_info.format(str(local_time), str(available), str(job_instance.time),
#                                             job_instance.title.encode('utf8'),
#                                             job_instance.url.encode('utf8'))
