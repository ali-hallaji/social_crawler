# Python import
from bson.json_util import dumps

# Core Import
from core import toLog
from config.settings import period_years
from services.plugins.crawler.libs.func_tools import divide_datetime
from services.rpc_core.query_handler import send_request


def initial_executer():

    # Run crawler
    create_bulk_jobs_from_dates()


def create_bulk_jobs_from_dates():
    tuple_month_list = divide_datetime(period_years)

    for item in tuple_month_list:
        args = (dumps(item[0]), dumps(item[1]))
        result = send_request('crawler.main_robot', args)

        msg = "Crawler jobs from: {0} | to: {1}".format(item[0], item[1])
        msg += "{0}".format(str(result))
        toLog(msg, 'jobs')
