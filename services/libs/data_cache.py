import threading
from datetime import datetime, timedelta
from core import toLog


lock = threading.Lock()


class KeyExpiredError(KeyError):
    pass


def __hax():

    class NoArg:
        pass

    return NoArg()


NoArg = __hax()


class DataCache(object):
    """
        Cache which has data that expires after a given period of time.

        Usage:
            >>> dc = DataCache(timedelta(0, 5, 0)) #expire in 5 seconds
            >>> dc[4] = 3
            >>> dc[4]
            3
            >>> import time
            >>> time.sleep(5)
            >>> dc[4]
            DataCache: Key 4 expired
            Traceback (most recent call last):
              File "<pyshell#5>", line 1, in <module>
                dc[4]
              File "datacache.py", line 35, in __getitem__
                raise KeyExpiredError(key)
            KeyExpiredError: 4
            >>>

    """

    def __init__(self, defaultExpireTime=timedelta(1, 0, 0), dbg=True):
        self.defaultExpireTime = defaultExpireTime
        self.cache = {}
        self.dbg = dbg
        self.processExpires = True

    def setProcessExpires(self, b):
        self.processExpires = b

    def __getitem__(self, key):
        c = self.cache[key]
        n = datetime.now()

        if n - c['timestamp'] < c['expireTime'] or not self.processExpires:
            return c['data']

        msg = 'Deleted << "{0}" >> object from << "{1}" >> DataCache!!!'
        toLog(msg.format(self.cache[key], self.__name__), 'object')

        del self.cache[key]

        if self.dbg:
            toLog('DataCache: Key %s expired' % repr(key), 'object')

        raise KeyExpiredError(key)

    def __contains__(self, key):

        try:
            self[key]
            return True

        except KeyError:
            return False

    def __setitem__(self, key, val):

        lock.acquire()
        try:
            self.cache[key] = {
                'data': val,
                'timestamp': datetime.now(),
                'expireTime': self.defaultExpireTime
            }

        finally:
            # Always called, even if exception is raised in try block
            lock.release()

    def items(self):
        keys = list(self.cache)

        for k in keys:

            try:
                val = self[k]
                yield (k, val)

            except:
                pass

    def get(self, key, default=NoArg, expired=NoArg):

        try:
            return self[key]

        except KeyExpiredError:

            if expired is NoArg and default is not NoArg:
                return default

            if expired is NoArg:
                return None

            return expired

        except KeyError:
            if default is NoArg:
                return None
            return default

    def set(self, key, val, expireTime=None):

        if expireTime is None:
            expireTime = self.defaultExpireTime

        lock.acquire()
        try:

            self.cache[key] = {
                'data': val,
                'timestamp': datetime.now(),
                'expireTime': expireTime
            }
        finally:
            # Always called, even if exception is raised in try block
            lock.release()

    def tryremove(self, key):

        lock.acquire()
        try:
            if key in self.cache:
                del self.cache[key]
                return True
        finally:
            # Always called, even if exception is raised in try block
            lock.release()

        return False

    def getTotalExpireTime(self, key):
        """Get the total amount of time the key will be in the cache for"""
        c = self.cache[key]
        return c['expireTime']

    def getExpirationTime(self, key):
        """Return the datetime when the given key will expire"""
        c = self.cache[key]
        return c['timestamp'] + c['expireTime']

    def getTimeRemaining(self, key):
        """Get the time left until the item will expire"""
        return self.getExpirationTime(key) - datetime.now()

    def getTimestamp(self, key):
        return self.cache[key]['timestamp']

    def __len__(self):
        return len(self.cache)

    def setName(self, name):
        self.__name__ = str(name)
