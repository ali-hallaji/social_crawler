# python import
from bson.json_util import loads
from bson.json_util import dumps

# Core Services import
from core.db import cursor_self
from services.libs.async_call import asynchronous
from services.libs.register import register


@register
class SetSharedMem:
    """
        SetSharedMem
    """
    __name__ = 'set_to_share_memory'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.set_to_share_memory'
    documentation = """
        Fetch your data from shared_memory

        e.g:
        main.set_to_share_memory(key, data) > bool

        Keyword arguments:
        data         -- Dumps of dict
        key          -- String

        ACL:
            TODO:
    """

    @asynchronous
    def run(self, key, data):

        doc = {'_type': key, 'value': loads(data)}
        insert = cursor_self.definitions.insert(doc)

        return dumps(insert)


SetSharedMem()
