import logging

from apscheduler import events
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.twisted import TwistedScheduler

from config.settings import CORE_ID
from config.settings import MONGO_HOST_SELF
from config.settings import MONGO_PORT_SELF
from config.settings import coalesce
from config.settings import local_tz
from config.settings import max_instances
from config.settings import path_apscheduler
from config.settings import processpool_executor
from config.settings import threadpool_executor
from core import toLog
from core.log_manager.log_levels import setup_logger

setup_logger('apscheduler', path_apscheduler, logging.DEBUG)

executors = {
    'default': ThreadPoolExecutor(threadpool_executor),
    'processpool': ProcessPoolExecutor(processpool_executor)
}

job_defaults = {
    'coalesce': coalesce,
    'max_instances': max_instances
}

scheduler = TwistedScheduler(timezone=local_tz)
scheduler.add_jobstore(
    'mongodb',
    host=MONGO_HOST_SELF,
    port=MONGO_PORT_SELF,
    collection=CORE_ID
)

scheduler.add_executor(
    ThreadPoolExecutor(threadpool_executor), 'default'
)

scheduler.add_executor(
    ProcessPoolExecutor(processpool_executor), 'processpool'
)

scheduler.start()


def job_logger(event):
    if event.code > 512:
        toLog('Job {}, code {}, run time {}, return value {}, exception {}'.format(
            event.job_id, event_code_translator(event.code),
            event.scheduled_run_time, event.retval, event.exception
        ), 'jobs')

    elif event > 64:
        toLog('Event {} for job {} happenend'.format(event_code_translator(event.code), event.job_id), 'jobs')

    else:
        toLog('Event {} happenend'.format(event_code_translator(event.code)), 'jobs')


def event_code_translator(code):
    event_dict = {
        1: 'EVENT_SCHEDULER_START',
        2: 'EVENT_SCHEDULER_SHUTDOWN',
        4: 'EVENT_EXECUTOR_ADDED',
        8: 'EVENT_EXECUTOR_REMOVED',
        16: 'EVENT_JOBSTORE_ADDED',
        32: 'EVENT_JOBSTORE_REMOVED',
        64: 'EVENT_ALL_JOBS_REMOVED',
        128: 'EVENT_JOB_ADDED',
        256: 'EVENT_JOB_REMOVED',
        512: 'EVENT_JOB_MODIFIED',
        1024: 'EVENT_JOB_EXECUTED',
        2048: 'EVENT_JOB_ERROR',
        4096: 'EVENT_JOB_MISSED'
    }

    return event_dict.get(code, None)

scheduler.add_listener(job_logger, events.EVENT_ALL)

