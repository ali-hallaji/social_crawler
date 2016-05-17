# Python Import
from bson.json_util import dumps
from collections import defaultdict
from twisted.internet import reactor
# from txjsonrpc import jsonrpclib
from txjsonrpc.web import jsonrpc

# Core Import
from core import toLog
from config.settings import installed_component
from core.manager.initialize_functions import initial_executer
from core.patterns.class_singleton import singleton
from services.component.component_generator import generate_class_component


@singleton
class CoreServices(jsonrpc.JSONRPC):
    """
        This is base API that for communicate with VIRGOLE.

        This is used to get the header info so that we can test
        authentication.
    """
    global plugin_functions
    plugin_functions = []

    def __init__(self, user='', password=''):
        jsonrpc.JSONRPC.__init__(self)

        # Settings Component
        self.set_name_spacing()

        # Initial some functions
        reactor.callInThread(initial_executer, )

    def set_name_spacing(self):
        """
            Please set your component in this here.
            This is follow namespace concept in your API service.
            Usage:
                Please call your component after API cursor when connection is
                connected to the server.
        """
        for component in installed_component:

            try:
                klass = generate_class_component(component)
                self.putSubHandler(component, klass())

            except Exception as e:
                toLog("{}".format(e), 'error')
                msg = "Component {} Faild to register!".format(component)
                toLog(msg, 'error')

    # def parseJsonRPC(self, request):
    #     """
    #         Initial parse for your request.
    #         Please set & checked your token request in this here.
    #     """
        # content = request.content.read()
        # if not content and request.method == 'GET' and 'request' in request.args:
        #     content = request.args['request'][0]
        # parse = jsonrpclib.loads(content)
        # token = parse.get('token', 0)
        # method = parse.get('method')
        # id = parse.get('id')
        # version = parse.get('jsonrpc')
        # method_list = ['get_token', 'authorize', 'check_expire']
        # ip = request.getClientIP()
        # if token == 0 and method in method_list:
        #     pass

    # def render(self, request):
    #     return jsonrpc.JSONRPC.render(self, request)

    def jsonrpc_authinfo(self):
        return (self.request.getUser(), self.request.getPassword())

    def jsonrpc_methodHelp(self, method):
        method = self._getFunction(method)
        return dumps(getattr(method.im_class, 'documentation', ''))

    jsonrpc_methodHelp.signature = [['string', 'string']]

    def jsonrpc_listMethods(self):
        """
        Return a list of the method names implemented by this server.
        """
        functions = []
        new_list = []
        dd = defaultdict(list)

        for item in plugin_functions:
            split_func_name = item.split('.')
            new_list.append({split_func_name[0]: [split_func_name[1]]})

        [dd[item.keys()[0]].append(item.values()[0][0]) for item in new_list]
        new_dict = dict(dd)
        todo = [(self, '')]

        while todo:
            obj, prefix = todo.pop(0)
            functions.extend([prefix + name for name in obj._listFunctions()])
            todo.extend([(obj.getSubHandler(name), prefix + name + obj.separator)
                         for name in obj.getSubHandlerPrefixes()])

        functions.sort()
        for item in new_dict:
            functions.append({item: new_dict[item]})

        return functions

    jsonrpc_listMethods.signature = [['array']]
