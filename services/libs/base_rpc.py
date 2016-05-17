from txjsonrpc.web import jsonrpc

from config.settings import BASE_DIR
from services.libs import plugin_handler
from services.libs.plugin_loader import PluginLoader


class BaseRPC(jsonrpc.JSONRPC):

    def __init__(self):
        jsonrpc.JSONRPC.__init__(self)

    def loadPlugins(self, module):
        load_module = __import__("services")
        classobj = getattr(load_module.plugins, module)
        classobj.loadFlag()

        loader = PluginLoader()
        arg = BASE_DIR + '/services/plugins/{}'.format(module)

        return loader.initPlugins(arg)

    def setPlugins(self):
        """
        This method set all plugins
        """
        plugins = plugin_handler.initHandler().getPlugins()

        for plugin in plugins[self.__class__.__name__].values():
            plugin_name = 'jsonrpc_%s' % plugin.__name__
            setattr(self, plugin_name, plugin.run)
