# Python import
import time
import random
# from apscheduler.jobstores.base import ConflictingIdError
from bson.json_util import dumps

# Core Import
from config.settings import keyword_list
from config.settings import max_page_crawl
from config.settings import period_years
from core import toLog
# from core.generals.scheduler import scheduler
from services.plugins.crawler.libs.func_tools import crawl_search
from services.plugins.crawler.libs.func_tools import divide_datetime
from services.rpc_core.query_handler import send_request


def initial_executer():

    # Run crawler with api
    # create_bulk_jobs_from_dates()
    # create_bulk_jobs_from_dates()
    update_crawl_data()
    # try:
    #     scheduler.add_job(
    #         create_bulk_jobs_from_dates,
    #         'interval',
    #         hours=24,
    #         id='youtube_api'
    #     )

    # except ConflictingIdError as e:
    #     print e

    # # Run crawler without api
    # try:
    #     scheduler.add_job(
    #         create_crawl_job,
    #         'interval',
    #         hours=24,
    #         id='youtube_without_api'
    #     )
    # create_crawl_job()

    # except ConflictingIdError as e:
    #     print e


def create_bulk_jobs_from_dates():
    tuple_month_list = divide_datetime(period_years)

    for item in tuple_month_list:
        args = (dumps(item[1]), dumps(item[0]))
        result = send_request('crawler.main_robot', args)

        msg = "Crawler jobs from: {0} | to: {1}".format(item[1], item[0])
        msg += "{0}".format(str(result))
        toLog(msg, 'jobs')


def create_crawl_job():
    time_list = [2, 2.12, 3, 2.2, 2.75, 2.6, 1.1, 2.31, 2.5]
    msg = "start crawler jobs"
    toLog(msg, 'jobs')

    for i in range(1, max_page_crawl + 1):

        for case in keyword_list:
            crawl_search(case, i)
            time.sleep(random.choice(time_list))

    msg = "end crawler jobs"
    toLog(msg, 'jobs')


def update_crawl_data():
    result = send_request('crawler.cycle_update', '')
    msg = "Start new jobs for update crawling data."
    msg += " {0}".format(str(result))
    toLog(msg, 'jobs')
