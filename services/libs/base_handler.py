# python import
import traceback
from functools import wraps
from txjsonrpc import jsonrpclib

# Core Services import
from core import toLog


class JsonRPCFault(jsonrpclib.Fault):

    def __init__(self, msg, code=401):
        jsonrpclib.Fault.__init__(self, code, msg)
        msg = "Message: {0}, Code: {1}".format(msg, code)
        toLog(msg, 'error')


class ExpiredKeyError(JsonRPCFault):

    def __init__(self, msg, code=406):
        JsonRPCFault.__init__(self, code, msg)


class DoseNotExist(JsonRPCFault):

    def __init__(self, msg, code=407):
        JsonRPCFault.__init__(self, code, msg)


class LoginFaild(JsonRPCFault):

    def __init__(self, msg, code=403):
        JsonRPCFault.__init__(self, code, msg)


class GeneralError(JsonRPCFault):

    def __init__(self, msg, code=500):
        JsonRPCFault.__init__(self, code, msg)


class DuplicationKeyError(JsonRPCFault):

    def __init__(self, msg, code=408):
        JsonRPCFault.__init__(self, code, msg)


class IndexErrorKey(JsonRPCFault):

    def __init__(self, msg, code=409):
        JsonRPCFault.__init__(self, code, msg)


class PermissionDeniedIP(JsonRPCFault):

    def __init__(self, msg, code=410):
        JsonRPCFault.__init__(self, code, msg)


class KeyErrorField(JsonRPCFault):

    def __init__(self, msg, code=411):
        JsonRPCFault.__init__(self, code, msg)


class Unauthorized(JsonRPCFault):

    def __init__(self, msg, code=401):
        JsonRPCFault.__init__(self, code, msg)


class SearchKeyError(JsonRPCFault):

    def __init__(self, msg, code=412):
        JsonRPCFault.__init__(self, code, msg)


class WrongToken(JsonRPCFault):

    def __init__(self, msg, code=413):
        JsonRPCFault.__init__(self, code, msg)


class BCodeError(JsonRPCFault):

    def __init__(self, msg, code=414):
        JsonRPCFault.__init__(self, code, msg)


class NotFoundClient(JsonRPCFault):

    def __init__(self, msg, code=415):
        JsonRPCFault.__init__(self, code, msg)


class NameErrorDB(JsonRPCFault):

    def __init__(self, msg, code=416):
        JsonRPCFault.__init__(self, code, msg)


class BigDataError(JsonRPCFault):

    def __init__(self, msg, code=420):
        JsonRPCFault.__init__(self, code, msg)


class DeletionError(JsonRPCFault):

    def __init__(self, msg, code=417):
        JsonRPCFault.__init__(self, code, msg)


class WrongType(JsonRPCFault):

    def __init__(self, msg, code=418):
        JsonRPCFault.__init__(self, code, msg)


class OutOfTypePattern(JsonRPCFault):

    def __init__(self, msg, code=419):
        JsonRPCFault.__init__(self, code, msg)


class ErrorInsertation(JsonRPCFault):

    def __init__(self, msg, code=421):
        JsonRPCFault.__init__(self, code, msg)


class ParamsError(JsonRPCFault):

    def __init__(self, msg, code=422):
        JsonRPCFault.__init__(self, code, msg)


class ErrorGeneratorFromRaise(object):

    def __init__(self, msg, type_error):
        self.msg = msg
        self.type_error = type_error

    def generateException(self):
        release_error = eval('%s' % self.type_error)(self.msg)
        toLog(str(release_error), 'error')
        return release_error


class ConnectionFailed(Exception):
    pass


def exception_handler(cls):

    @wraps(cls)
    def checking(*args, **kwargs):
        """
           Exception Handler
        """
        try:
            return cls(*args, **kwargs)

        except Exception as e:

            toLog(traceback.format_exc(), 'error')
            msg = str(e)

            if 'run()' in msg:
                name = args[0].__full_name__
                msg = msg.replace('run()', "Function {0}()".format(name))

            toLog(msg, 'error')

            try:
                error = ErrorGeneratorFromRaise(
                    msg, e.type_error).generateException()
                return error

            except:
                error = GeneralError(msg)
                return error

    return checking
