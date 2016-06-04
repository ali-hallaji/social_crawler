# python import
from bson.json_util import dumps

# Core Services import
from services.libs.async_call import asynchronous
from services.libs.register import register
from services.plugins.crawler.libs.soundcloud_func import soundcloud_update


@register
class SoundCloudUpdate:
    """
        SoundCloudUpdate
    """
    __name__ = 'update_soundcloud'
    __namespace__ = 'CrawlerComponent'
    __full_name__ = 'crawler.update_soundcloud'
    documentation = """

        e.g:
        main.update_soundcloud() > bool

        Keyword arguments:

        ACL:
            TODO:
    """

    @asynchronous
    def run(self):

        soundcloud_update()
        return dumps(True)


SoundCloudUpdate()
