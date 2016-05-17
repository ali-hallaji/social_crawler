# import datetime
import time

from functools import wraps
from twisted.internet import reactor
# from twisted.internet.threads import deferToThread
from twisted.internet.threads import deferToThreadPool
from txjsonrpc.web.jsonrpc import with_activity_log


from base_handler import exception_handler
# from config.settings import CORE_NAME
from config.settings import DEBUG
from core import toLog
# from core.db import cursor_local
from core.threading_pool.core_thread import get_twisted_pool as pool


def asynchronous(cls):

    cls = exception_handler(cls)
    with_activity_log(cls)

    @wraps(cls)
    def async(*args, **kwargs):
        """
           This asynchronous call function.
        """

        args = list(args)
        username = args.pop(1)
        address = args.pop(1)
        args = tuple(args)

        # start time
        ts = time.time()

        # Pass to defer
        worker = deferToThreadPool(reactor, pool(), cls, *args, **kwargs)
        # worker = deferToThread(cls, *args, **kwargs)

        # Handle defer
        worker.addCallback(timeit, username, address, ts, *args)
        worker.addErrback(to_log_error)

        return worker

    return async


def timeit(result, username, address, ts, *args):

    if DEBUG:
        # End of time execute work
        func_name = args[0].__class__.__full_name__
        te = time.time()

        msg = "RPC Call username: {0}  -- time: {1:2.4f} sec -- "
        msg += "func: {2} -- address: {3} -- args: {4}"
        msg = msg.format(username, te - ts, func_name, address, args[1:])
        toLog(msg, 'request')

        # set_activity_log(username, address, func_name, args[1:])

    return result


def to_log_error(failure):
    toLog(str(failure), 'error')


# def set_activity_log(username, address, func_name, args):
#     activity_log_list = activity_log.keys()

#     if (func_name in activity_log_list) and (username != CORE_NAME):
#         now = datetime.datetime.now()
#         doc = {'created_date': now}
#         doc['username'] = username
#         doc['api_name'] = func_name
#         doc['address'] = address
#         doc['action'] = activity_log[func_name]
#         doc['args'] = args

#         cursor_local.activity_log.insert(doc)
