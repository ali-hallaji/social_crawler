# python import
from bson.json_util import dumps

# Core Services import
from services.libs.async_call import asynchronous
from services.libs.register import register
from services.plugins.crawler.libs.soundcloud_func import soundcloud_runner


@register
class SoundCloudRunner:
    """
        SoundCloudRunner
    """
    __name__ = 'start'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.start'
    documentation = """

        e.g:
        main.start() > bool

        Keyword arguments:

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        soundcloud_runner()
        return dumps(True)


SoundCloudRunner()
