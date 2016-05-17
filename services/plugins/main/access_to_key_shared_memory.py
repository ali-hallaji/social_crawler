# python import
from bson.json_util import dumps

# Core Services import
from core.db import cursor_self
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class FetchSharedMem:
    """
        FetchSharedMem
    """
    __name__ = 'access_shared_memory'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.access_shared_memory'
    documentation = """
        Fetch your data from shared_memory

        e.g:
        main.access_shared_memory(key) > object

        Keyword arguments:
        key         -- String

        ACL:
            TODO:
    """

    @asynchronous
    def run(self, key):

        criteria = {'_type': key}
        obj = cursor_self.definitions.find_one(criteria)

        if obj:
            return dumps(obj['value'])

        else:
            return dumps(None)


FetchSharedMem()
