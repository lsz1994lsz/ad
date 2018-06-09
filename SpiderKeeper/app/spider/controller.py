# -*- coding: utf-8 -*-
import datetime
# from app.spider import guard_server_memory
from app.spider import *
from app.util import *
import sys
import os
import tempfile
import config
import flask_restful
import requests
from app.schedulers.common import run_spider_job, schedule_log_cron
# import time
import re
import threading
from flask import Blueprint, request
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask_restful_swagger import swagger
from werkzeug.utils import secure_filename

from app import db, api, agent, app
from app.spider.model import JobInstance, Project, JobExecution, SpiderInstance, CronJobInstance, JobRunType

api_spider_bp = Blueprint('spider', __name__)

'''
========= api =========
'''


class ProjectCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list projects',
        parameters=[])
    def get(self):
        return [project.to_dict() for project in Project.query.all()]

    @swagger.operation(
        summary='add project',
        parameters=[{
            "name": "project_name",
            "description": "project name",
            "required": True,
            "paramType": "form",
            "dataType": 'string'
        }])
    def post(self):
        project_name = request.form['project_name']
        project = Project()
        project.project_name = project_name
        db.session.add(project)
        db.session.commit()
        return project.to_dict()


class SpiderCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list spiders',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        project = Project.find_project_by_id_common(project_id)
        return [spider_instance.to_dict() for spider_instance in
                SpiderInstance.query.filter_by(project_id=project_id).all()]


class SpiderDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='spider detail',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_id",
            "description": "spider instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id, spider_id):
        spider_instance = SpiderInstance.query.filter_by(project_id=project_id, id=spider_id).first()
        return spider_instance.to_dict() if spider_instance else abort(404)

    @swagger.operation(
        summary='run spider',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_id",
            "description": "spider instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_arguments",
            "description": "spider arguments",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "tags",
            "description": "spider tags",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "spider desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }])
    def put(self, project_id, spider_id):
        spider_instance = SpiderInstance.query.filter_by(project_id=project_id, id=spider_id).first()
        if not spider_instance: abort(404)
        job_instance = JobInstance()
        job_instance.spider_name = spider_instance.spider_name
        job_instance.project_id = project_id
        job_instance.spider_arguments = request.form.get('spider_arguments')
        job_instance.desc = request.form.get('desc')
        job_instance.tags = request.form.get('tags')
        job_instance.run_type = JobRunType.ONETIME
        job_instance.priority = request.form.get('priority', 0)
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
        return True


JOB_INSTANCE_FIELDS = [column.name for column in JobInstance.__table__.columns]
JOB_INSTANCE_FIELDS.remove('id')
JOB_INSTANCE_FIELDS.remove('date_created')
JOB_INSTANCE_FIELDS.remove('date_modified')


class JobCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job instance',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return [job_instance.to_dict() for job_instance in
                JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]

    @swagger.operation(
        summary='add job instance',
        notes="json keys: <br>" + "<br>".join(JOB_INSTANCE_FIELDS),
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_name",
            "description": "spider_name",
            "required": True,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "spider_arguments",
            "description": "spider_arguments,  split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "tags",
            "description": "tags , split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "run_type",
            "description": "onetime/periodic",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "cron_minutes",
            "description": "@see http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_hour",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_week",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }])
    def post(self, project_id):
        post_data = request.form
        if post_data:
            job_instance = JobInstance()
            job_instance.spider_name = post_data['spider_name']
            job_instance.project_id = project_id
            job_instance.spider_arguments = post_data.get('spider_arguments')
            job_instance.desc = post_data.get('desc')
            job_instance.tags = post_data.get('tags')
            job_instance.run_type = post_data['run_type']
            job_instance.priority = post_data.get('priority', 0)
            if job_instance.run_type == "periodic":
                job_instance.cron_minutes = post_data.get('cron_minutes') or '0'
                job_instance.cron_hour = post_data.get('cron_hour') or '*'
                job_instance.cron_day_of_month = post_data.get('cron_day_of_month') or '*'
                job_instance.cron_day_of_week = post_data.get('cron_day_of_week') or '*'
                job_instance.cron_month = post_data.get('cron_month') or '*'
            db.session.add(job_instance)
            db.session.commit()
            return True


class JobDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='update job instance',
        notes="json keys: <br>" + "<br>".join(JOB_INSTANCE_FIELDS),
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "job_id",
            "description": "job instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_name",
            "description": "spider_name",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "spider_arguments",
            "description": "spider_arguments,  split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "tags",
            "description": "tags , split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "run_type",
            "description": "onetime/periodic",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "cron_minutes",
            "description": "@see http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_hour",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_week",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "enabled",
            "description": "-1 / 0, default: 0",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "status",
            "description": "if set to 'run' will run the job",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }

        ])
    def put(self, project_id, job_id):
        post_data = request.form
        if post_data:
            job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_id).first()
            if not job_instance: abort(404)
            job_instance.spider_arguments = post_data.get('spider_arguments') or job_instance.spider_arguments
            job_instance.priority = post_data.get('priority') or job_instance.priority
            job_instance.enabled = post_data.get('enabled', 0)
            job_instance.cron_minutes = post_data.get('cron_minutes') or job_instance.cron_minutes
            job_instance.cron_hour = post_data.get('cron_hour') or job_instance.cron_hour
            job_instance.cron_day_of_month = post_data.get('cron_day_of_month') or job_instance.cron_day_of_month
            job_instance.cron_day_of_week = post_data.get('cron_day_of_week') or job_instance.cron_day_of_week
            job_instance.cron_month = post_data.get('cron_month') or job_instance.cron_month
            job_instance.desc = post_data.get('desc', 0) or job_instance.desc
            job_instance.tags = post_data.get('tags', 0) or job_instance.tags
            db.session.commit()
            if post_data.get('status') == 'run':
                agent.start_spider(job_instance)
            return True


class JobExecutionCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job execution status',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return JobExecution.list_jobs(project_id)


class JobExecutionDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='stop job',
        notes='',
        parameters=[
            {
                "name": "project_id",
                "description": "project id",
                "required": True,
                "paramType": "path",
                "dataType": 'int'
            },
            {
                "name": "job_exec_id",
                "description": "job_execution_id",
                "required": True,
                "paramType": "path",
                "dataType": 'string'
            }
        ])
    def put(self, project_id, job_exec_id):
        job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
        if job_execution:
            agent.cancel_spider(job_execution)
            return True


api.add_resource(ProjectCtrl, "/api/projects")
api.add_resource(SpiderCtrl, "/api/projects/<project_id>/spiders")
api.add_resource(SpiderDetailCtrl, "/api/projects/<project_id>/spiders/<spider_id>")
api.add_resource(JobCtrl, "/api/projects/<project_id>/jobs")
api.add_resource(JobDetailCtrl, "/api/projects/<project_id>/jobs/<job_id>")
api.add_resource(JobExecutionCtrl, "/api/projects/<project_id>/jobexecs")
api.add_resource(JobExecutionDetailCtrl, "/api/projects/<project_id>/jobexecs/<job_exec_id>")

'''
========= Router =========
'''


@app.errorhandler(403)
def action_forbidden(error):
    print 'error is ', error
    return render_template('403.html', message=error)


@app.before_request
def intercept_no_project():
    if request.path.find('/project//') > -1:
        flash("create project first")
        return redirect("/project/manage", code=302)


@app.context_processor
def inject_common():
    return dict(now=datetime.datetime.now(),
                servers=agent.servers)


@app.context_processor
def inject_project():
    project_context = dict()
    server_list = config.SERVERS
    project_context['server_list'] = server_list
    project_context['project_list_of_servers'] = Project.project_list_of_servers()
    project_context['project_list'] = Project.query.all()
    project_context['gelonghui_running'] = JobInstance.list_all_gelonghui_running()
    if project_context['project_list'] and not session.get('project_id'):
        project = Project.query.first()
        session['project_id'] = project.id
    if session.get('project_id'):
        project_context['project'] = Project.find_project_by_id_common(session['project_id'])
        project_context['spider_list'] = [spider_instance.to_dict() for spider_instance in
                                          SpiderInstance.query.filter_by(project_id=session['project_id']).all()]
    else:
        project_context['project'] = {}
    return project_context


@app.context_processor
def utility_processor():
    def timedelta(end_time, start_time):
        '''

        :param end_time:
        :param start_time:
        :param unit: s m h
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

    return dict(timedelta=timedelta, readable_time=readable_time)


@app.route("/")
def index():
    if not session.get('role'):
        return render_template('index.html')
    if session.get('role') == 10:
        project = Project.query.first()
        if project:
            return redirect("/project/%s/job/dashboard" % project.id, code=302)
        return redirect("/project/manage", code=302)
    if session.get('role') == 1:
        project = Project.query.first()
        if project:
            return redirect("/project/%s/operator/dashboard" % project.id, code=302)
        abort(403, u'运营项目尚未创建,请联系后台')


@app.route("/logout")
def logout():
    session.pop('role')
    return redirect('/')


@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    passwd = request.form.get('passwd')
    if username == 'super' and passwd == 'super':
        session['role'] = 10
        project = Project.query.first()
        if project:
            return redirect("/project/%s/job/dashboard" % project.id, code=302)
        return redirect("/project/manage", code=302)
    elif username == 'admin' and passwd == 'admin':
        session['role'] = 1
        project = Project.query.first()
        if project:
            return redirect("/project/%s/operator/dashboard" % project.id, code=302)
        abort(403, u'运营项目尚未创建,请联系后台')
    else:
        abort(403, u'密码错误')


@app.route("/project/<project_id>")
def project_index(project_id):
    session['project_id'] = project_id
    if session.get('role') == 10:
        return redirect("/project/%s/job/dashboard" % project_id, code=302)
    if session.get('role') == 1:
        return redirect("/project/%s/operator/dashboard" % project_id, code=302)


@app.route("/project/create", methods=['post'])
def project_create():
    project_name = request.form['project_name'].rstrip()
    server = request.form.get("server")
    index_of_servers = int(request.form.get("index_of_servers"))
    project = Project()
    project.project_name = project_name
    project.server = server
    project.index_of_servers = index_of_servers
    db.session.add(project)
    db.session.commit()
    session['project_id'] = project.id
    print 'create project {}'.format(project_name.encode('utf8'))
    return redirect("/project/%s/spider/deploy" % project.id, code=302)


@app.route("/project/<int:project_id>/delete")
def project_delete(project_id):
    running_job_ids = set([job.id for job in scheduler.get_jobs()])
    # do not delete first project
    if int(project_id) == 1:
        # action_forbidden('hello')
        abort(403, u'必须保留运营的刷量项目, 并确保该项目数据库中project_id=1')
    job_status = JobExecution.list_jobs(project_id)
    job_count = len(job_status['PENDING']) + len(job_status['RUNNING'])
    if job_count > 0:
        abort(403, u'必须等待从属于该project的所有spider跑完并写入数据库才能删除该project')
    job_instances = db.session.query(JobInstance).filter(JobInstance.project_id == project_id,
                                                         JobInstance.is_deleted == 0).all()
    # must remove all cron jobs
    if job_instances:
        for job in job_instances:
            if job.enabled == 0:
                abort(403, u'请先暂停该project下的所有周期性任务')
    project = Project.find_project_by_id_common(project_id)
    # job_id = project.project_name
    # if job_id in running_job_ids:
    #     try:
    #         scheduler.remove_job(job_id)
    #         app.logger.info('[drop_spider_job][job_id:%s]' % job_id)
    #     except Exception as e:
    #         app.logger.error(
    #             '[drop_spider_job] failed [job_id:%s]' % job_id)
    agent.delete_project(project)
    project.is_deleted = 1
    db.session.commit()
    # db.session.delete(project)
    # db.session.query(JobExecution).filter(JobExecution.project_id == project_id).delete()
    # db.session.query(SpiderInstance).filter(SpiderInstance.project_id == project_id).delete()

    return redirect("/", code=302)


@app.route("/project/manage")
def project_manage():
    if session.get('role') == 1:
        return redirect('/')
    return render_template("project_manage.html")


@app.route("/project/<project_id>/job/dashboard")
def job_dashboard(project_id):
    if not session.get('role'):
        return redirect('/')
    if session.get('role') == 1:
        return redirect('/')
    project = Project.find_project_by_id_common(project_id)
    if not project:
        return redirect('/')
    index_of_servers = project.index_of_servers
    scrapyd_server = project.server
    return render_template("job_dashboard.html", job_status=JobExecution.list_jobs(project_id),
                           index_of_servers=index_of_servers, scrapyd_server=scrapyd_server)


@app.route("/project/<project_id>/operator/dashboard")
def operator_dashboard(project_id):
    project = Project.find_project_by_id_common(project_id)
    if not project:
        return redirect('/')
    index_of_servers = project.index_of_servers
    scrapyd_server = project.server
    return render_template("operator_dashboard.html", job_status=JobExecution.list_jobs(project_id),
                           index_of_servers=index_of_servers, scrapyd_server=scrapyd_server)


@app.route("/project/<project_id>/job/periodic")
def job_periodic(project_id):
    project = Project.find_project_by_id_common(project_id)
    if not project:
        return redirect('/')
    if session.get('role') == 1:
        return redirect('/')
    index_of_servers = project.index_of_servers
    scrapyd_server = project.server
    job_instance_list = [job_instance.to_dict() for job_instance in
                         JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]
    return render_template("job_periodic.html",
                           job_instance_list=job_instance_list, index_of_servers=index_of_servers,
                           scrapyd_server=scrapyd_server,)


@app.route("/project/<project_id>/job/add", methods=['post'])
def job_add(project_id):
    job_status = JobExecution.list_jobs(project_id)
    job_count = len(job_status['PENDING']) + len(job_status['RUNNING'])
    if 'win' in sys.platform:
        job_limit = 14
    else:
        job_limit = 4
    if int(project_id) == 1:
        if job_count > job_limit - 1:
            print 'job_count', job_count
            abort(403, u'同一时间的刷量数不能超过四个')
            # return redirect(request.referrer)
    project = Project.find_project_by_id_common(project_id)
    scrapyd_server_index = int(request.form['scrapyd_server_index'])
    print 'scrapyd_server_index', scrapyd_server_index
    job_instance = JobInstance()
    job_instance.spider_name = request.form['spider_name']
    job_instance.project_id = project_id
    job_instance.running_on = project.server

    pattern_time = '^[1-9]{1}\d{0,5}$'
    url_time = request.form.get('time')
    time_result = re.match(pattern_time, url_time)
    if time_result is None:
        abort(403, u'time格式错误')
        # return redirect(request.referrer)

    # try:
    #     url_time = int(request.form.get('time'))
    # except ValueError:
    #     # abort(403, u'time必须全为数字且不能为空')
    #     return redirect(request.referrer)
    # if url_time <= 0:
    #     # abort(403, u'time不能小于零')
    #     return redirect(request.referrer)
    # if request.form['time'][0] == '0':
    #     # abort(403, u'time不能为零开头')
    #     return redirect(request.referrer)
    # if '.' in request.form['time']:
    #     # abort(403, u'time不能为有小数点')
    #     return redirect(request.referrer)

    url = request.form.get('url')
    # url_of_caifu = ['http://caifuhao.eastmoney.com', 'https://caifuhao.eastmoney.com',
    #                 'http://emcreative.eastmoney.com', 'https://emcreative.eastmoney.com']
    # url_of_sohu = ['http://www.sohu.com', 'https://www.sohu.com', 'http://m.sohu.com', 'https://m.sohu.com']
    # url_of_gelonghui = ['http://www.gelonghui.com', 'http://www.gelonghui.com',
    #                     'http://gelonghui.com', 'https://gelonghui.com',
    #                     'http://m.gelonghui.com', 'https://m.gelonghui.com']
    # url_of_zhongjin = ['http://mp.cnfol.com', 'https://mp.cnfol.com']
    # url_prefix = tuple(['None'] + url_of_caifu + url_of_sohu + url_of_gelonghui + url_of_zhongjin)
    # if not request.form['url'].startswith(url_prefix):
    #     abort(403, u'url前缀不在规定范围内')
    # if ' ' in request.form['url'].strip():
    #     abort(403, u'url中间不能有空格')
    if int(project_id) == 1:

        pattern_sohu = '^(https://)www.sohu.com/a/\d{9}_\d{6}\s*$'
        pattern_sohu_1 = '^(http://)www.sohu.com/a/\d{9}_\d{6}\s*$'
        pattern_caifu_1 = '^(http://)caifuhao.eastmoney.com/news/\d{23}\s*$'
        pattern_caifu_2 = '^(http://)emcreative.eastmoney.com/Fortune/V/Share_ArticleDetail/\d{23}\s*$'
        pattern_zhongjin = '^(http://)mp.cnfol.com/article/\d{7}\s*$'
        pattern = '|'.join([pattern_sohu, pattern_sohu_1, pattern_caifu_1, pattern_caifu_2, pattern_zhongjin])
        url_result = re.match(pattern, url)
        if url_result is None:
            abort(403, u'url不在规定范围内')
            # return redirect(request.referrer)

        total_time_in_mysql = JobExecution.total_time_of_running_and_pending(project_id)
        # print 'total_time_in_mysql', total_time_in_mysql
        total_time = total_time_in_mysql + int(request.form['time'])
        # print 'total_time', total_time
        if total_time > 100000:
            abort(403, u'刷量总数不能超过十万')
            # return redirect(request.referrer)

    job_instance.url = url.strip()
    job_instance.time = int(url_time)
    job_instance.title = request.form['title']
    job_instance.priority = request.form.get('priority', 0)
    job_instance.run_type = request.form['run_type']

    if job_instance.run_type == JobRunType.ONETIME:
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
        app.logger.info('[common_run][run_spider_job][project:%s][spider_name:%s][job_instance_id:%s]' % (
            job_instance.project_id, job_instance.spider_name, job_instance.id))
    if job_instance.run_type == JobRunType.PERIODIC:
        cron_instance = CronJobInstance()
        job_instance.cron_minutes = request.form.get('cron_minutes') or '0'
        job_instance.cron_hour = request.form.get('cron_hour') or '*'
        job_instance.cron_day_of_month = request.form.get('cron_day_of_month') or '*'
        job_instance.cron_day_of_week = request.form.get('cron_day_of_week') or '*'
        job_instance.cron_month = request.form.get('cron_month') or '*'

        cron_instance.spider_name = request.form['spider_name']
        cron_instance.project_id = project_id
        cron_instance.running_on = project.server
        cron_instance.url = request.form['url'].strip()
        cron_instance.time = int(request.form['time'].strip())
        cron_instance.title = request.form['title']
        cron_instance.priority = request.form.get('priority', 0)
        cron_instance.run_type = request.form['run_type']
        cron_instance.cron_minutes = request.form.get('cron_minutes') or '0'
        cron_instance.cron_hour = request.form.get('cron_hour') or '*'
        cron_instance.cron_day_of_month = request.form.get('cron_day_of_month') or '*'
        cron_instance.cron_day_of_week = request.form.get('cron_day_of_week') or '*'
        cron_instance.cron_month = request.form.get('cron_month') or '*'
        # set cron exp manually
        if request.form.get('cron_exp'):
            job_instance.cron_minutes, job_instance.cron_hour, job_instance.cron_day_of_month, \
            job_instance.cron_month, cron_day_of_week = request.form['cron_exp'].split()
            job_instance.cron_day_of_week_real = cron_day_of_week

            cron_instance.cron_minutes, cron_instance.cron_hour, cron_instance.cron_day_of_month, \
            cron_instance.cron_month, cron_day_of_week = request.form['cron_exp'].split()
            cron_instance.cron_day_of_week_real = cron_day_of_week
            if u'*' in cron_day_of_week:
                job_instance.cron_day_of_week = cron_day_of_week

                cron_instance.cron_day_of_week = cron_day_of_week
            elif u',' in cron_day_of_week:
                a = cron_day_of_week.split(u',')
                b = [int(i) - 1 for i in a]
                c = [str(i) for i in b]
                d = u','.join(c)
                job_instance.cron_day_of_week = d

                cron_instance.cron_day_of_week = d
            elif u'-' in cron_day_of_week:
                a = cron_day_of_week.split(u'-')
                b = [int(i) - 1 for i in a]
                c = [str(i) for i in b]
                d = u'-'.join(c)
                job_instance.cron_day_of_week = d

                cron_instance.cron_day_of_week = d
            else:
                job_instance.cron_day_of_week = unicode(int(cron_day_of_week) - 1)

                cron_instance.cron_day_of_week = unicode(int(cron_day_of_week) - 1)

        db.session.add(job_instance)
        db.session.commit()

        cron_instance.date_created = job_instance.date_created
        cron_instance.job_id = job_instance.id
        db.session.add(cron_instance)
        db.session.commit()
        run_cron(job_instance, run_spider_job)
        schedule_log_cron()

    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/jobexecs/<job_exec_id>/stop")
def job_stop(project_id, job_exec_id):
    job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
    agent.cancel_spider(job_execution)
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/jobexecs/<job_exec_id>/log")
def job_log(project_id, job_exec_id):
    job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
    res = requests.get(agent.log_url(job_execution))
    res.encoding = 'utf8'
    raw = res.text
    return render_template("job_log.html", log_lines=raw.split('\n'))


@app.route("/project/<project_id>/job/<job_instance_id>/run")
def job_run(project_id, job_instance_id):
    job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_instance_id).first()
    agent.start_spider(job_instance)
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/job/<job_instance_id>/remove")
def job_remove(project_id, job_instance_id):
    job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_instance_id).first()
    date_created = job_instance.date_created
    cron_instance = CronJobInstance.find_job_instance_by_date_created(date_created)
    remove_cron(job_instance)
    # db.session.query(JobExecution).filter(JobExecution.job_instance_id == job_instance_id)\
    #     .delete(synchronize_session=False)
    # job_execution_all = JobExecution.list_job_by_job_instance_id(int(job_instance_id))
    # db.session.delete(job_execution_all)
    job_instance.is_deleted = 1
    # db.session.delete(job_instance)
    db.session.delete(cron_instance)
    db.session.commit()
    # schedule_log_cron()
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/job/<job_instance_id>/switch")
def job_switch(project_id, job_instance_id):
    job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_instance_id).first()
    date_created = job_instance.date_created
    cron_instance = CronJobInstance.find_job_instance_by_date_created(date_created)
    if job_instance.enabled == 0:
        print 'remove cron'
        remove_cron(job_instance)
        job_instance.enabled = -1
        cron_instance.enabled = -1
        db.session.commit()
    elif job_instance.enabled == -1:
        print 'start cron'
        run_cron(job_instance, run_spider_job)
        job_instance.enabled = 0
        cron_instance.enabled = 0
        db.session.commit()
    # schedule_log_cron()
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/spider/dashboard")
def spider_dashboard(project_id):
    if session.get('role') == 1:
        return redirect('/')
    # print "spider_instance_list before"
    spider_instance_list = SpiderInstance.list_spiders(project_id)
    # print "spider_instance_list after", spider_instance_list
    return render_template("spider_dashboard.html",
                           spider_instance_list=spider_instance_list)


@app.route("/project/<project_id>/spider/deploy")
def spider_deploy(project_id):
    if session.get('role') == 1:
        return redirect('/')
    project = Project.find_project_by_id_common(project_id)
    scrapyd_server = project.server
    index_of_servers = project.index_of_servers
    return render_template("spider_deploy.html", project=project,
                           scrapyd_server=scrapyd_server, index_of_servers=index_of_servers)


@app.route("/project/<project_id>/spider/upload", methods=['post'])
def spider_egg_upload(project_id):
    scrapyd_servers = agent.spider_service_instances
    scrapyd_server_index = int(request.form.get('scrapyd_server_index'))
    scrapyd_server = scrapyd_servers[scrapyd_server_index]
    project = Project.find_project_by_id_common(project_id)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.referrer)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer)
    if file:
        filename = secure_filename(file.filename)
        dst = os.path.join(tempfile.gettempdir(), filename)
        file.save(dst)
        project.server = scrapyd_server
        project.index_of_servers = scrapyd_server_index
        db.session.commit()
        agent.deploy(project, dst, scrapyd_server_index)
        print 'hello deploy success'
        flash('deploy success!')

        # sync sk_spider
        _index = project.index_of_servers
        spider_instance_list = agent.get_spider_list(project, _index)
        SpiderInstance.update_spider_instances(project.id, spider_instance_list)
    return redirect(request.referrer)


@app.route("/project/<project_id>/project/stats")
def project_stats(project_id):
    if session.get('role') == 1:
        return redirect('/')
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("project_stats.html", run_stats=run_stats)


@app.route("/project/<project_id>/server/stats")
def service_stats(project_id):
    if session.get('role') == 1:
        return redirect('/')
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("server_stats.html", run_stats=run_stats)


@app.route("/project/gelonghui",)
def gelonghui():
    if not session.get('role'):
        return redirect('/')
    if not Project.query.all():
        abort(403, u'请先创建一个project')
    return render_template("gelonghui.html")


@app.route("/project/gelonghui/ssh", methods=['POST'])
def gelonghui_ssh():
    pattern_1 = '^(https://www.)gelonghui.com/p/\d{6}\s*$'
    pattern_1_1 = '^(http://www.)gelonghui.com/p/\d{6}\s*$'
    pattern_2 = '^(https://www.)gelonghui.com/column/article/\d{6}\s*$'
    pattern_2_1 = '^(http://www.)gelonghui.com/column/article/\d{6}\s*$'
    pattern_3 = '^(https://)m.gelonghui.com/article/\d{6}\s*$'
    pattern_3_1 = '^(http://)m.gelonghui.com/article/\d{6}\s*$'
    pattern = '|'.join([pattern_1, pattern_1_1, pattern_2, pattern_2_1, pattern_3, pattern_3_1])
    url = request.form.get('url')
    result = re.match(pattern, url)
    if result is None:
        abort(403, u'url不在规定范围内')
        # return redirect(request.referrer)
    # if not request.form['url'].startswith(('http://', 'https://')):
    #     abort(403, u'url格式错误,必须以http://或者https://开头')
    # url_prefix = ('http://www.gelonghui.com', 'https://www.gelonghui.com',
    #               'http://gelonghui.com', 'https://gelonghui.com')
    # if not request.form['url'].startswith(url_prefix):
    #     abort(403, u'url前缀不在规定范围内')
    # if ' ' in request.form['url'].rstrip():
    #     abort(403, u'url中间不能有空格')
    try:
        url_time = int(request.form['time'])
    except ValueError:
        abort(403, u'time必须全为数字且不能为空')
        # return redirect(request.referrer)
    if url_time <= 0:
        abort(403, u'time不能小于零')
        # return redirect(request.referrer)
    if request.form['time'][0] == '0':
        abort(403, u'time不能为零开头')
        # return redirect(request.referrer)
    if '.' in request.form['time']:
        abort(403, u'time不能为有小数点')
        # return redirect(request.referrer)

    ge_url = url.strip()
    ge_time = url_time
    ge_title = request.form.get('title')
    t = threading.Thread(target=gelong, args=(ge_url, ge_time, ge_title))
    t.start()
    return redirect('/')


@app.route("/gelonghui/<job_instance_id>/stop")
def gelonghui_job_stop(job_instance_id):
    job_instance_ge = JobInstance.find_job_instance_by_id_common(int(job_instance_id))
    job_execution_ge = JobExecution()
    job_execution_ge.project_id = job_instance_ge.project_id
    job_execution_ge.job_instance_id = job_instance_ge.id
    job_execution_ge.create_time = datetime.datetime.now()
    job_execution_ge.start_time = datetime.datetime.now()
    job_execution_ge.running_on = 'http://121.40.77.248:6800'
    job_execution_ge.service_job_execution_id = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    job_execution_ge.running_status = 3
    job_execution_ge.mark_ge = 1
    job_execution_ge.end_time = datetime.datetime.now()
    job_instance_ge.over_ge = 1
    db.session.add(job_execution_ge)
    db.session.commit()

    url = job_instance_ge.url
    total_time = job_instance_ge.time
    ssh_kill(url, total_time)
    return redirect(request.referrer, code=302)


@app.route("/gelonghui/<job_instance_id>/remove")
def gelonghui_job_remove(job_instance_id):
    if session.get('role') != 10:
        abort(403, u'权限不够')
    job_instance_ge = JobInstance.find_job_instance_by_id_common(int(job_instance_id))
    job_execution_ge = JobExecution()
    job_execution_ge.project_id = job_instance_ge.project_id
    job_execution_ge.job_instance_id = job_instance_ge.id
    job_execution_ge.create_time = datetime.datetime.now()
    job_execution_ge.start_time = datetime.datetime.now()
    job_execution_ge.running_on = 'http://121.40.77.248:6800'
    job_execution_ge.service_job_execution_id = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    job_execution_ge.running_status = 2
    job_execution_ge.mark_ge = 1
    job_execution_ge.end_time = datetime.datetime.now()
    job_instance_ge.over_ge = 1
    db.session.add(job_execution_ge)
    db.session.commit()
    return redirect(request.referrer, code=302)


# @app.route("/project/<int:project_id>/job/log_cron/remove")
# def log_cron_remove(project_id):
#     if session.get('role') != 10:
#         abort(403)
#     cron_id = Project.find_project_by_id_common(project_id).project_name
#     remove_log_cron(cron_id)
