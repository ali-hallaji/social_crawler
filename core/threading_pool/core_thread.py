# python import
import random
from twisted.internet import reactor
from Queue import Queue
from threading import Thread
from twisted.python.threadpool import ThreadPool


# Core Services import
from config.settings import background_process_thread_pool
from config.settings import main_min_thread as min_t
from config.settings import main_max_thread as max_t
from core import toLog


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception, e:
                toLog('Thread Error: %s' % e, 'error')
            self.tasks.task_done()


class ThreadPoolPython:
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kwargs):
        """Add a task to the queue"""

        key = random.randint(1000, 100000)
        msg = "Calling background process with id: {0} -- func: {1}"
        toLog(msg.format(key, func.__name__), 'jobs')

        self.tasks.put((func, args, kwargs))

        toLog("End of background process with id: {0}".format(key), 'jobs')

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


def get_pool():
    pool = ThreadPoolPython(background_process_thread_pool)
    return pool


def get_twisted_pool():
    global pool

    try:
        return pool

    except:
        pool = ThreadPool(minthreads=min_t, maxthreads=max_t, name='core')
        pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        return pool
