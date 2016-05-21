# python import
import datetime

from bson.json_util import dumps
# from twisted.internet import reactor

# Core Services import
from config.settings import local_tz
from config.settings import update_crawling_interval
from core.generals.scheduler import scheduler
from services.libs.async_call import asynchronous
from services.libs.register import register
from services.plugins.crawler.libs.func_tools import start_updating_jobs


@register
class CycleUpdate:
    """
        CycleUpdate
    """
    __name__ = 'cycle_update'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.cycle_update'
    documentation = """

        e.g:
        main.cycle_update() > bool

        Keyword arguments:

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        scheduler.add_job(
            start_updating_jobs,
            'interval',
            minutes=update_crawling_interval,
            args=[],
            timezone=local_tz
        )
        # reactor.callInThread(start_updating_jobs, )

        return dumps(True)


CycleUpdate()
