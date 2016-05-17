# Python import
import logging
import logging.handlers

# Core Import
from config.settings import backup_count
from config.settings import max_bytes
from config.settings import path_db
from config.settings import path_debug
from config.settings import path_error
from config.settings import path_apscheduler
from config.settings import path_object
from config.settings import path_jobs
from config.settings import path_request
from config.settings import path_service
from dependency import singleton

# logging.basicConfig()


def setup_logger(logger_name, log_file, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.disabled = False

    date_format = '%Y-%m-%d %H:%M:%S'
    date_string = '%(asctime)s - %(message)s'
    formatter = logging.Formatter(date_string, datefmt=date_format)

    file_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=max_bytes, backupCount=backup_count)
    logger.addHandler(file_handler)
    file_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(file_handler)

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)


@singleton
class LoggerError(object):

    def __init__(self):
        log_type = 'core_services_error'
        setup_logger(log_type, path_error, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices Error Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerApscheduler(object):

    def __init__(self):
        log_type = 'core_services_apscheduler'
        setup_logger(log_type, path_apscheduler, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices Apsheduler Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerObject(object):

    def __init__(self):
        log_type = 'core_services_object'
        setup_logger(log_type, path_object, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices Object Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerService(object):

    def __init__(self):
        log_type = 'core_services_service'
        setup_logger(log_type, path_service, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices Service Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerDB(object):

    def __init__(self):
        log_type = 'core_services_db'
        setup_logger(log_type, path_db, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices db Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerJobs(object):

    def __init__(self):
        log_type = 'core_services_jobs'
        setup_logger(log_type, path_jobs, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices jobs Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerRequest(object):

    def __init__(self):
        log_type = 'core_services_request'
        setup_logger(log_type, path_request, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices request Logs ***')

    def getLog(self):
        return self.log


@singleton
class LoggerDebug(object):

    def __init__(self):
        log_type = 'core_services_debug'
        setup_logger(log_type, path_debug, logging.INFO)
        self.log = logging.getLogger(log_type)
        self.log.info('*** Start CoreServices Debug Logs ***')

    def getLog(self):
        return self.log
