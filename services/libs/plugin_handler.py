# python import
# Core Services import

plugin_handler = None


class Plugin:
    """
       This Class Hold all plugins
       All of plugins are located in plugins directory
    """

    def __init__(self):
        # this variable holds all plugins {plugin_name:value,...}
        self.__plugins = dict()

    def registerPlugin(self, plugin):
        """
           This method register plugin that have register method
        """
        if plugin.__namespace__ in self.__plugins:
            self.__plugins[plugin.__namespace__][plugin.__name__] = plugin
        else:
            self.__plugins[plugin.__namespace__] = {}
            self.__plugins[plugin.__namespace__][plugin.__name__] = plugin

    def getPlugins(self):
        return self.__plugins


def getHandler():
    global plugin_handler
    return plugin_handler


def initHandler():
    global plugin_handler
    if plugin_handler is None:
        plugin_handler = Plugin()

    return plugin_handler
