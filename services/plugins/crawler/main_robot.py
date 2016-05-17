# python import
from bson.json_util import dumps
from bson.json_util import loads
from twisted.internet import reactor

# Core Services import
from services.libs.async_call import asynchronous
from services.libs.register import register
from services.plugins.crawler.libs.func_tools import execute_batch


@register
class MainRobot:
    """
        MainRobot
    """
    __name__ = 'main_robot'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.main_robot'
    documentation = """
        Fetch your data from shared_memory

        e.g:
        main.main_robot(key, data) > bool

        Keyword arguments:
        data         -- Dumps of dict
        key          -- String

        ACL:
            TODO:
    """

    @asynchronous
    def run(self, _from, _to, keyword=''):
        _from = loads(_from)
        _to = loads(_to)
        criteria = {'max_results': 50, 'q': keyword}

        reactor.callInThread(execute_batch, _from, _to, criteria)

        return dumps(True)


MainRobot()
