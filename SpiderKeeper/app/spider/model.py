import datetime
from sqlalchemy import desc, create_engine
# from sqlalchemy.orm import sessionmaker
from app import db, Base
from config import SERVERS
import sys

# if 'win' in sys.platform:
#     engine = create_engine('mysql://root:123@localhost:3306/SpiderKeeper', isolation_level="READ UNCOMMITTED")
#     # session_maker = sessionmaker(bind=engine)
#     # SQLALCHEMY_DATABASE_URI = 'mysql://218.244.138.88:13456/' + 'SpiderKeeper' + '?user=spiderdb&passwd=Cqmyg321'
# else:
#     from requests import get
#     ip = get('https://api.ipify.org').text
#     if ip == u'101.37.174.208':
#         engine = create_engine('mysql://root:123@localhost:3306/SpiderKeeper', isolation_level="READ UNCOMMITTED")
#         # session_maker = sessionmaker(bind=engine)
#     else:
#         engine = create_engine('mysql://spiderdb:Cqmyg321@218.244.138.88:13456/SpiderKeeper',
#                                isolation_level="READ UNCOMMITTED")
        # session_maker = sessionmaker(bind=engine)


class Project(Base):
    __tablename__ = 'sk_project'

    project_name = db.Column(db.String(50), unique=True)
    server = db.Column(db.Text)
    index_of_servers = db.Column(db.INTEGER)
    is_deleted = db.Column(db.INTEGER, default=0, index=True)  # 0/1

    @classmethod
    def load_project(cls, project_list):
        for project in project_list:
            existed_project = cls.query.filter_by(project_name=project.project_name).first()
            if not existed_project:
                db.session.add(project)
                db.session.commit()

    # @classmethod
    # def find_project_by_id(cls, project_id):
    #     connection = engine.connect()
    #     result = connection.execute("select * from sk_project where id={}".format(project_id)).first()
    #     connection.close()
    #     return result
        # return Project.query.filter_by(id=project_id).first()

    @classmethod
    def find_all_project(cls):
        # db.session.flush()
        db.session.commit()
        return cls.query.all()

    @classmethod
    def find_project_by_id_common(cls, project_id):
        # session = session_maker()
        # cursor = session.query(Project)
        # result = cursor.query_filter(id=project_id).first()
        # return result
        # return db.session.query(Project).filter_by(id=project_id).first()
        # return Project.query.filter_by(id=project_id).one()
        # db.session.commit()
        # db.session.flush()
        db.session.commit()
        return cls.query.get(project_id)

    @classmethod
    def find_project_id_by_name(cls, project_name):
        project = Project.query.filter_by(project_name=project_name).first()
        return project.id

    @classmethod
    def project_list_of_servers(cls):
        from collections import defaultdict
        project_list = defaultdict(list)
        server_list = SERVERS
        for server in server_list:
            pro_list = cls.query.filter_by(server=server).all()
            project_list[server].extend(pro_list)
        return project_list

    def to_dict(self):
        return {
            "project_id": self.id,
            "project_name": self.project_name,
            "is_deleted": self.is_deleted,
        }


class SpiderInstance(Base):
    __tablename__ = 'sk_spider'

    spider_name = db.Column(db.String(100))
    project_id = db.Column(db.INTEGER, nullable=False)
    scrapyd_server = db.Column(db.Text)

    @classmethod
    def update_spider_instances(cls, project_id, spider_instance_list):
        print 'project_id:', project_id
        print 'spider_instance_list:', spider_instance_list
        for spider_instance in spider_instance_list:
            existed_spider_instance = cls.query.filter_by(project_id=project_id,
                                                          spider_name=spider_instance.spider_name).first()
            if not existed_spider_instance:
                db.session.add(spider_instance)
                db.session.commit()
            for spider in cls.query.filter_by(project_id=project_id).all():
                existed_spider = any(
                    spider.spider_name == s.spider_name
                    for s in spider_instance_list
                )
                if not existed_spider:
                    print 'commit 2'
                    db.session.delete(spider)
                    db.session.commit()

    @classmethod
    def list_spider_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    def to_dict(self):
        return dict(spider_instance_id=self.id,
                    spider_name=self.spider_name,
                    project_id=self.project_id)

    @classmethod
    def list_spiders(cls, project_id):
        sql_last_runtime = '''
            select * from (select a.spider_name,b.date_created from sk_job_instance as a
                left join sk_job_execution as b
                on a.id = b.job_instance_id
                order by b.date_created desc) as c
                group by c.spider_name, c.date_created
            '''
        sql_avg_runtime = '''
            select a.spider_name,avg(end_time-start_time) from sk_job_instance as a
                left join sk_job_execution as b
                on a.id = b.job_instance_id
                where b.end_time is not null
                group by a.spider_name
            '''
        last_runtime_list = dict(
            (spider_name, last_run_time) for spider_name, last_run_time in db.engine.execute(sql_last_runtime))
        avg_runtime_list = dict(
            (spider_name, avg_run_time) for spider_name, avg_run_time in db.engine.execute(sql_avg_runtime))
        res = []
        for spider in cls.query.filter_by(project_id=project_id).all():
            last_runtime = last_runtime_list.get(spider.spider_name)
            res.append(dict(spider.to_dict(),
                            **{'spider_last_runtime': last_runtime if last_runtime else '-',
                               'spider_avg_runtime': avg_runtime_list.get(spider.spider_name)
                               }))
        return res


class JobPriority:
    def __init__(self):
        pass

    LOW, NORMAL, HIGH, HIGHEST = range(-1, 3)


class JobRunType:
    def __init__(self):
        pass
    ONETIME = 'onetime'
    PERIODIC = 'periodic'


class JobInstance(Base):
    __tablename__ = 'sk_job_instance'

    spider_name = db.Column(db.String(100), nullable=False, index=True)
    project_id = db.Column(db.INTEGER, nullable=False, index=True)
    # tags = db.Column(db.Text)  # job tag(split by , )
    url = db.Column(db.String(100), nullable=False)
    running_on = db.Column(db.String(100), nullable=False)
    time = db.Column(db.INTEGER, nullable=False)
    title = db.Column(db.String(100))
    # spider_arguments = db.Column(db.Text)  # job execute arguments(split by , ex.: arg1=foo,arg2=bar)
    priority = db.Column(db.INTEGER)
    # desc = db.Column(db.Text)
    cron_minutes = db.Column(db.String(20), default="0")
    cron_hour = db.Column(db.String(20), default="*")
    cron_day_of_month = db.Column(db.String(20), default="*")
    cron_day_of_week = db.Column(db.String(20), default="*")
    cron_day_of_week_real = db.Column(db.String(20), default="*")
    cron_month = db.Column(db.String(20), default="*")
    enabled = db.Column(db.INTEGER, default=0)  # 0/-1
    scrapyd_alive = db.Column(db.INTEGER, default=1, index=True)  # 1/0
    mark_ge = db.Column(db.INTEGER, default=0, index=True)  # 0/1
    over_ge = db.Column(db.INTEGER, default=0, index=True)  # 0/1
    is_deleted = db.Column(db.INTEGER, default=0, index=True)  # 0/1
    run_type = db.Column(db.String(20))  # periodic/onetime

    def to_dict(self):
        return dict(
            job_instance_id=self.id,
            spider_name=self.spider_name,
            # tags=self.tags.split(',') if self.tags else None,
            # spider_arguments=self.spider_arguments,
            title=self.title,
            running_on=self.running_on,
            url=self.url,
            time=self.time,
            priority=self.priority,
            # desc=self.desc,
            cron_minutes=self.cron_minutes,
            cron_hour=self.cron_hour,
            cron_day_of_month=self.cron_day_of_month,
            cron_day_of_week=self.cron_day_of_week,
            cron_day_of_week_real=self.cron_day_of_week_real,
            cron_month=self.cron_month,
            enabled=self.enabled == 0,
            scrapyd_alive=self.scrapyd_alive,
            run_type=self.run_type,
            mark_ge=self.mark_ge,
            over_ge=self.over_ge,
            is_deleted=self.is_deleted,
        )

    @classmethod
    def list_job_instance_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    # @classmethod
    # def find_job_instance_by_id(cls, job_instance_id):
    #     # return cls.query.filter_by(id=job_instance_id).first()
    #     connection = engine.connect()
    #     result = connection.execute("select * from sk_job_instance where id={}".format(job_instance_id)).first()
    #     connection.close()
    #     return result

    @classmethod
    def find_job_instance_by_id_common(cls, job_instance_id):
        # session = session_maker()
        # cursor = session.query(JobInstance)
        # result = cursor.query_filter(id=job_instance_id).first()
        # return result
        # return db.session.query(JobInstance).filter_by(id=job_instance_id).first()
        # return cls.query.filter_by(id=job_instance_id).one()
        # db.session.flush()
        db.session.commit()
        return cls.query.get(job_instance_id)

    @classmethod
    def detail_of_error_executions(cls):
        detail_of_executions = list()
        list_of_error_execution = JobExecution.list_of_error_execution()
        list_of_error_instance = [cls.find_job_instance_by_id(i.id) for i in list_of_error_execution]
        for job in list_of_error_instance:
            tup = (job.title, job.url, job.time)
            detail_of_executions.append(tup)
        return list(set(detail_of_executions))

    @classmethod
    def list_all_scrapyd_die_job_instances(cls):
        return JobInstance.query.filter_by(project_id=1, scrapyd_alive=0).all()

    @classmethod
    def list_all_gelonghui_running(cls):
        return JobInstance.query.filter_by(mark_ge=1, over_ge=0).all()


class SpiderStatus:
    def __init__(self):
        pass

    PENDING, RUNNING, FINISHED, CANCELED = range(4)


class JobExecution(Base):
    __tablename__ = 'sk_job_execution'

    project_id = db.Column(db.INTEGER, nullable=False, index=True)
    service_job_execution_id = db.Column(db.String(50), nullable=False, index=True)
    job_instance_id = db.Column(db.INTEGER, nullable=False, index=True)
    create_time = db.Column(db.DATETIME)
    start_time = db.Column(db.DATETIME)
    end_time = db.Column(db.DATETIME)
    running_status = db.Column(db.INTEGER, default=SpiderStatus.PENDING, index=True)
    running_on = db.Column(db.Text)
    # occur_error = db.Column(db.INTEGER, default=0)  # 0/1
    scrapyd_alive = db.Column(db.INTEGER, default=1, index=True)  # 1/0
    stopped = db.Column(db.INTEGER, default=0)  # 0/1
    mark_ge = db.Column(db.INTEGER, default=0, index=True)  # 0/1
    read_over = db.Column(db.INTEGER, default=0, index=True)  # 0/1

    def to_dict(self):
        job_instance = JobInstance.query.filter_by(id=self.job_instance_id).first()
        return {
            'project_id': self.project_id,
            'job_execution_id': self.id,
            'job_instance_id': self.job_instance_id,
            'service_job_execution_id': self.service_job_execution_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'running_status': self.running_status,
            'running_on': self.running_on,
            'stopped': self.stopped,
            'scrapyd_alive': self.scrapyd_alive,
            'mark_ge': self.mark_ge,
            'read_over': self.read_over,
            'job_instance': job_instance.to_dict() if job_instance else {}
        }

    @classmethod
    def list_job_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    @classmethod
    def list_job_by_job_instance_id(cls, job_instance_id):
        return cls.query.filter_by(job_instance_id=job_instance_id).all()

    @classmethod
    def find_job_by_service_id(cls, service_job_execution_id):
        return cls.query.filter_by(service_job_execution_id=service_job_execution_id).first()

    @classmethod
    def find_job_of_not_read_over(cls, job_instance_id):
        return cls.query.filter_by(job_instance_id=job_instance_id, read_over=0).first()

    @classmethod
    def list_job_by_service_ids(cls, service_job_execution_ids):
        return cls.query.filter(cls.service_job_execution_id.in_(service_job_execution_ids)).all()

    @classmethod
    def list_uncomplete_job_common(cls, project_id):
        # return cls.query.filter(cls.project_id == project_id, cls.running_status != SpiderStatus.FINISHED,
        #                         cls.running_status != SpiderStatus.CANCELED).all()
        # db.session.commit()
        # db.session.flush()
        db.session.commit()
        return cls.query.filter(cls.project_id == project_id, cls.running_status.in_([SpiderStatus.PENDING,
                                                                                      SpiderStatus.RUNNING])).all()

    # @classmethod
    # def list_uncomplete_job(cls, project_id):
    #     connection = engine.connect()
    #     result = connection.execute("select * from sk_job_instance where "
    #                                 "project_id={} and running_status in (0, 1) ".format(project_id)).all()
    #     connection.close()
    #     return result

    @classmethod
    def list_jobs(cls, project_id, each_status_limit=100):
        result = dict()
        result['PENDING'] = [job_execution.to_dict() for job_execution in
                             JobExecution.query.filter_by(project_id=project_id,
                                                          running_status=SpiderStatus.PENDING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit)]
        result['RUNNING'] = [job_execution.to_dict() for job_execution in
                             JobExecution.query.filter_by(project_id=project_id,
                                                          running_status=SpiderStatus.RUNNING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit)]
        result['COMPLETED'] = [job_execution.to_dict() for job_execution in
                               JobExecution.query.filter(JobExecution.project_id == project_id).filter(
                                   (JobExecution.running_status == SpiderStatus.FINISHED) | (
                                       JobExecution.running_status == SpiderStatus.CANCELED)).order_by(
                                   desc(JobExecution.end_time)).limit(each_status_limit)]
        return result

    @classmethod
    def list_executions(cls, project_id, each_status_limit=100):
        result = dict()
        result['PENDING'] = JobExecution.query.filter_by(project_id=project_id,
                                                         running_status=SpiderStatus.PENDING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit).all()

        result['RUNNING'] = JobExecution.query.filter_by(project_id=project_id,
                                                         running_status=SpiderStatus.RUNNING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit).all()

        # result['COMPLETED'] = JobExecution.query.filter(JobExecution.project_id == project_id).filter(
        #                            (JobExecution.running_status == SpiderStatus.FINISHED) | (
        #                                    JobExecution.running_status == SpiderStatus.CANCELED)).order_by(
        #                            desc(JobExecution.date_modified)).limit(each_status_limit).all()

        return result

    @classmethod
    def list_all_executions(cls, each_status_limit=100):
        result = dict()
        result['PENDING'] = JobExecution.query.filter_by(running_status=SpiderStatus.PENDING, project_id=1).order_by(
            desc(JobExecution.date_modified)).limit(each_status_limit).all()

        result['RUNNING'] = JobExecution.query.filter_by(running_status=SpiderStatus.RUNNING, project_id=1).order_by(
            desc(JobExecution.date_modified)).limit(each_status_limit).all()

        return result

    @classmethod
    def list_all_scrapyd_die_executions(cls, each_status_limit=100):
        result = dict()
        result['PENDING'] = JobExecution.query.filter_by(project_id=1, running_status=SpiderStatus.PENDING,
                                                         scrapyd_alive=0).order_by(
            desc(JobExecution.date_modified)).limit(each_status_limit).all()

        result['RUNNING'] = JobExecution.query.filter_by(project_id=1, running_status=SpiderStatus.RUNNING,
                                                         scrapyd_alive=0).order_by(
            desc(JobExecution.date_modified)).limit(each_status_limit).all()

        return result

    @classmethod
    def list_run_stats_by_hours(cls, project_id):
        result = {}
        hour_keys = []
        last_time = datetime.datetime.now() - datetime.timedelta(hours=23)
        last_time = datetime.datetime(last_time.year, last_time.month, last_time.day, last_time.hour)
        for hour in range(23, -1, -1):
            time_tmp = datetime.datetime.now() - datetime.timedelta(hours=hour)
            hour_key = time_tmp.strftime('%Y-%m-%d %H:00:00')
            hour_keys.append(hour_key)
            result[hour_key] = 0  # init
        for job_execution in JobExecution.query.filter(JobExecution.project_id == project_id,
                                                       JobExecution.date_created >= last_time).all():
            hour_key = job_execution.create_time.strftime('%Y-%m-%d %H:00:00')
            result[hour_key] += 1
        return [dict(key=hour_key, value=result[hour_key]) for hour_key in hour_keys]

    @classmethod
    def find_first_running_job(cls, project_id):
        return JobExecution.query.filter_by(project_id=project_id, running_status=1).first()

    # @classmethod
    # def list_of_error_execution(cls):
    #     return JobExecution.query.filter(cls.occur_error == 1).all()

    @classmethod
    def total_time_of_running_and_pending(cls, project_id):
        total_time = list()
        result = cls.list_executions(project_id)
        pending = result.get('PENDING')
        running = result.get('RUNNING')
        if pending:
            for execution in pending:
                job_instance_id = execution.job_instance_id
                job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
                url_time = int(job_instance.time)
                total_time.append(url_time)
        if running:
            for execution in running:
                job_instance_id = execution.job_instance_id
                job_instance = JobInstance.find_job_instance_by_id_common(job_instance_id)
                url_time = int(job_instance.time)
                total_time.append(url_time)
        return sum(total_time)


class CronJobInstance(Base):
    __tablename__ = 'cron_job_instance'

    spider_name = db.Column(db.String(100), nullable=False, index=True)
    project_id = db.Column(db.INTEGER, nullable=False, index=True)
    job_id = db.Column(db.INTEGER, nullable=False, index=True)
    # tags = db.Column(db.Text)  # job tag(split by , )
    url = db.Column(db.String(100), nullable=False)
    running_on = db.Column(db.String(100), nullable=False)
    time = db.Column(db.INTEGER, nullable=False)
    title = db.Column(db.String(100))
    # spider_arguments = db.Column(db.Text)  # job execute arguments(split by , ex.: arg1=foo,arg2=bar)
    priority = db.Column(db.INTEGER)
    # desc = db.Column(db.Text)
    cron_minutes = db.Column(db.String(20), default="0")
    cron_hour = db.Column(db.String(20), default="*")
    cron_day_of_month = db.Column(db.String(20), default="*")
    cron_day_of_week = db.Column(db.String(20), default="*")
    cron_day_of_week_real = db.Column(db.String(20), default="*")
    cron_month = db.Column(db.String(20), default="*")
    enabled = db.Column(db.INTEGER, default=0)  # 0/-1
    scrapyd_alive = db.Column(db.INTEGER, default=1, index=True)  # 1/0
    mark_ge = db.Column(db.INTEGER, default=0, index=True)  # 0/1
    over_ge = db.Column(db.INTEGER, default=0, index=True)  # 0/1
    run_type = db.Column(db.String(20))  # periodic/onetime

    def to_dict(self):
        return dict(
            job_instance_id=self.id,
            job_id=self.job_id,
            spider_name=self.spider_name,
            # tags=self.tags.split(',') if self.tags else None,
            # spider_arguments=self.spider_arguments,
            title=self.title,
            running_on=self.running_on,
            url=self.url,
            time=self.time,
            priority=self.priority,
            # desc=self.desc,
            cron_minutes=self.cron_minutes,
            cron_hour=self.cron_hour,
            cron_day_of_month=self.cron_day_of_month,
            cron_day_of_week=self.cron_day_of_week,
            cron_day_of_week_real=self.cron_day_of_week_real,
            cron_month=self.cron_month,
            enabled=self.enabled == 0,
            scrapyd_alive=self.scrapyd_alive,
            run_type=self.run_type,
            mark_ge=self.mark_ge,
            over_ge=self.over_ge,
        )

    @classmethod
    def list_all_instance(cls):
        return cls.query.all()

    @classmethod
    def find_job_instance_by_id(cls, job_instance_id):
        # return cls.query.filter_by(id=job_instance_id).first()
        # db.session.commit()
        # db.session.flush()
        db.session.commit()
        return cls.query.get(job_instance_id)

    @classmethod
    def find_job_instance_by_date_created(cls, date_created):
        return cls.query.filter_by(date_created=date_created).first()
