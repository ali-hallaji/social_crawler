# python import
from bson.json_util import dumps

# Core Services import
from services.libs.async_call import asynchronous
from services.libs.register import register
from services.plugins.crawler.libs.migrate_to_mysql import yt_most_viewed


@register
class BackUp:
    """
        BackUp
    """
    __name__ = 'backup'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.backup'
    documentation = """

        e.g:
        crawler.backup() > bool

        Keyword arguments:

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        yt_most_viewed()
        return dumps(True)


BackUp()
