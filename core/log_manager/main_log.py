# Python Import
import inspect
import os
import pprint
import sys
import traceback

# Core Import
from config.settings import log_dir
from core.log_manager.log_levels import LoggerDB
from core.log_manager.log_levels import LoggerDebug
from core.log_manager.log_levels import LoggerError
from core.log_manager.log_levels import LoggerObject
from core.log_manager.log_levels import LoggerService
from core.log_manager.log_levels import LoggerRequest
from core.log_manager.log_levels import LoggerJobs
from core.log_manager.log_levels import LoggerApscheduler


class Logger(object):

    def __init__(self):

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def setLog(self, message, log_level='debug'):

        if log_level == 'debug':
            self.log = LoggerDebug().getLog()
            self.log.info(str(message))

        elif log_level == 'error':
            self.log = LoggerError().getLog()
            self.log.info(str(message))

        elif log_level == 'service':
            self.log = LoggerService().getLog()
            self.log.info(str(message))

        elif log_level == 'object':
            self.log = LoggerObject().getLog()
            self.log.info(str(message))

        elif log_level == 'db':
            self.log = LoggerDB().getLog()
            self.log.info(str(message))

        elif log_level == 'request':
            self.log = LoggerRequest().getLog()
            self.log.info(str(message))

        elif log_level == 'jobs':
            self.log = LoggerJobs().getLog()
            self.log.info(str(message))

        elif log_level == 'apscheduler':
            self.log = LoggerApscheduler().getLog()
            self.log.info(str(message))

        else:
            logException('"%s" is not valid name for log levels!' % log_level)

    def logDebug(self):
        return self.debug

    def logService(self):
        return self.service

    def logError(self):
        return self.error


def getExceptionText():
    """
        create and return text of last exception
    """
    _type, value, tback = sys.exc_info()
    frame_locals = {}

    if inspect.getinnerframes(tback) and inspect.getinnerframes(tback)[-1]:
        frame_locals = inspect.getinnerframes(tback)[-1][0].f_locals

    text = pprint.pformat(frame_locals)
    text += '\n'
    text += ''.join(traceback.format_exception(_type, value, tback))
    return text


def logException(extra_str=''):
    err_text = getExceptionText()
    toLog(str(extra_str) + '\n' + str(err_text), 'error')


def toLog(message, level='debug'):
    logger = Logger()
    logger.setLog(message, level)


__all__ = ['toLog', 'logException']
