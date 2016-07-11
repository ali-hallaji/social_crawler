# Python import
import random
import time
from twisted.internet import reactor
# from apscheduler.jobstores.base import ConflictingIdError
# from bson.json_util import dumps

# Core Import
from config.settings import hour_crawl
from config.settings import hour_update
from config.settings import keyword_list
from config.settings import local_tz
from config.settings import max_page_crawl
from config.settings import minute_crawl
from config.settings import minute_update
from core import toLog
from core.generals.scheduler import scheduler
from services.plugins.crawler.libs.func_tools import bulk_jobs_from_dates
from services.plugins.crawler.libs.func_tools import crawl_search
from services.plugins.crawler.libs.soundcloud_func import ssh_connection
from services.plugins.crawler.libs.func_tools import start_updating_jobs
# from services.plugins.crawler.libs.backup_scheduler import yt_most_viewed
# from config.settings import period_years
# from core.generals.scheduler import scheduler
# from services.plugins.crawler.libs.func_tools import divide_datetime
# from services.rpc_core.query_handler import send_request


def initial_executer():

    # Run crawler with api
    start_crawling()

    # Update crawl
    update_crawl_data()
    # yt_most_viewed()


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
    # delete_video()


def update_crawl_data():

    scheduler.add_job(
        start_updating_jobs,
        trigger='cron',
        hour=hour_update,
        minute=minute_update,
        args=[],
        timezone=local_tz
    )

    # result = send_request('crawler.cycle_update', '')
    msg = "Start new jobs for update crawling data."
    toLog(msg, 'jobs')


def start_crawling():
    reactor.callInThread(ssh_connection,)

    scheduler.add_job(
        bulk_jobs_from_dates,
        trigger='cron',
        hour=hour_crawl,
        minute=minute_crawl,
        args=[],
        timezone=local_tz
    )

    msg = "Start crawling."
    toLog(msg, 'jobs')
