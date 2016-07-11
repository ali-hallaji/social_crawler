# python import
# from bson.json_util import loads
from bson.json_util import dumps

# Core Services import
# from core.db import cursor
from services.plugins.crawler.libs.soundcloud_func import ssh_connection
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class SSHConnection:
    """
        SSHConnection
    """
    __name__ = 'ssh'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.ssh'
    documentation = """
        Fetch your data from shared_memory

        e.g:
        crawler.ssh() > bool

        Keyword arguments:
         --

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        ssh_connection()

        return dumps(True)


SSHConnection()
