# python import
from bson.json_util import dumps
from twisted.internet import reactor

# Core Services import
from services.libs.async_call import asynchronous
from services.libs.register import register
from services.plugins.crawler.libs.func_tools import max_views_count


@register
class GetMaxViews:
    """
        GetMaxViews
    """
    __name__ = 'max_count'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.max_count'
    documentation = """
        Fetch your data from shared_memory

        e.g:
        main.max_count() > bool

        Keyword arguments:
        data         -- Dumps of dict
        key          -- String

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):
        reactor.callInThread(max_views_count, )
        return dumps(True)


GetMaxViews()
