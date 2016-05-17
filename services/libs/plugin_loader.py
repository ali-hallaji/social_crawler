# python import
import imp
import os
import sys
import types


# Core Services import
from core import logException
from core import toLog


class PluginLoader:

    def initPluginsAndRegister(self, directory, mapping):
        """
            Load all plugins in directory and try to register plugin
            members using mapping
            directory(text) :   directory path to search for plugins

            mapping(dic)    :   a dict in format {Class: registerMethod}
                                all plugins are searched for children of
                                Classes, and upon find, pass it registerMethod
                                to get registered
        """
        modules = self.initPlugins(directory)

        for module in modules.itervalues():
            self.__registerModuleAttributes(module, mapping)

        return modules

    def initPlugins(self, directory):
        """
            directory(text): directory path to search for plugins
            return all loaded module object
            call init function of all *.py files in "directory"
            they must register themselves somewhere
            ex. user plugins should user plugins.registerUserPlugin
        """
        py_files = self.__getPyFiles(directory)
        modules = {}
        modules.update(self.__loadArchivedModules(directory))
        modules.update(self.__loadModules(py_files, directory))
        self.__callInits(modules)
        return modules

    def __registerModuleAttributes(self, module, mapping):
        """
            Find all attribute classes in module and register
            it in attribute factory attribute classes are inherited
            from attributNe parents available in mapping
        """
        toLog('RegisterModuleAttributes: processing module: %s' % module,
              'service')

        for obj_name in dir(module):
            obj = getattr(module, obj_name)

            if self.__isClass(obj):

                for klass in mapping:
                    toLog('RegisterModuleAttributes: '
                          'obj = %s klass: %s subclass = %s'
                          % (obj, klass, issubclass(obj, klass)),
                          'service')

                    if issubclass(obj, klass) and obj != klass:
                        mapping[klass](obj)

    def __isClass(self, obj):
        return isinstance(obj, types.ClassType)

    def __callInits(self, modules):
        """
            call init function of all modules in "modules" dict
        """
        for obj in modules.itervalues():

            try:

                if hasattr(obj, 'init'):
                    obj.init()

            except:
                toLog('PluginLoader.__callInits', 'error')

    def __loadModules(self, py_list, directory):
        """
            load and import all files in "file_list" in path "directory"
            return a dic of loaded modules in format {module_name: module_obj}
        """
        modules = {}
        for file_name in py_list:
            file = None
            try:
                module_name = file_name[:-3]              # remove trailing.py
                (file, pathname, desc) = imp.find_module(module_name,
                                                         [directory])
                modules[module_name] = imp.load_module(module_name,
                                                       file, pathname,
                                                       desc)
            except Exception as e:
                if file is not None:
                    file.close()
                logException('LoadModulesError: PluginLoader.__loadModules: ' '%s' % e)
        return modules

    def __getPyFiles(self, directory):
        """
            return list of all .py files in directory
        """
        return filter(lambda name: name.endswith('.py') or name.endswith('.so'),
                      self.__getFilesList(directory))

    def __getFilesList(self, directory):
        """
            return list of all files in "directory"
        """
        # TODO:get directory which running
        try:
            return os.listdir(directory)

        except OSError as e:
            toLog('PluginLoader.__getFilesList: %s' % e, 'error')
            return []

    def __loadArchivedModules(self, directory):
        """
            Look if there's any archived module available for this directory
        """
        # Start in here
        module = None

        if '' in sys.modules:
            module = sys.modules['']

        if module:

            if directory.endswith('rases'):
                return module.r

            elif directory.endswith('charge/attrs'):
                return module.c

        else:
            plugin = directory.split('/')[-1]
            module_name = 'services.plugins.{}.'.format(plugin)
            load_module = __import__(module_name, fromlist=["*"])
            module = {module_name: load_module}
            return module

        return {}
