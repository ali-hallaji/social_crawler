from core import toLog
from services.libs.base_rpc import BaseRPC


def generate_class_component(name):
    class_name = name.capitalize() + 'Component'

    class Raw(BaseRPC, object):

        def __init__(self):
            BaseRPC.__init__(self)
            load_module = __import__("services")
            classobj = getattr(load_module.plugins, name)
            load_flag = classobj.getFlag()

            if not load_flag:
                self.loadPlugins(name)

            self.setPlugins()
            toLog('<%s added to services>' % class_name, 'service')

    klass = type(class_name, (Raw, ), {})

    return klass


