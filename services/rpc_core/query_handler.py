from socket import error as socket_error

from bson.json_util import loads
from bson.objectid import ObjectId
from jsonrpclib import Server
from jsonrpclib import history
from jsonrpclib.jsonrpc import ProtocolError
from jsonrpclib.jsonrpc import random_id

from config import settings
from core import toLog
from services.libs.base_handler import ConnectionFailed


def get_server(host, port):
    server = Server('http://{0}:{1}'.format(host, port))
    return server


def select_send_request(host, port, *args):
    output = {'error': {}, 'result': {}}
    rpc_id = random_id()
    args = args + (rpc_id,)
    result = None

    try:
        result = get_server(host, port)._request(*args)

        if isinstance(result, str) or isinstance(result, unicode):

            try:
                output['result'] = loads(result)

            except ValueError:

                if ObjectId.is_valid(str(result)):
                    output['result'] = str(result)

                else:
                    raise

        elif isinstance(result, dict) or isinstance(result, list):
            output['result'] = result

        elif isinstance(result, bool):
            output['result'] = result

        elif not result:
            output['result'] = {}

        else:
            raise TypeError

    except Exception as e:
        message_error = 'Func: {}, Error Type: {}, Error: {}, Result: {}, Message: {}'.format(
                str(args[0]), type(e), handle_errors(e, rpc_id), result, str(e)
            )
        output['error'] = handle_errors(e, rpc_id), message_error
        toLog(message_error, 'error')

        if hasattr(e, 'strerror') and (e.strerror == "No route to host"):
            msg = "RPC Connection Failed: The Core server is unavailable."
            msg += "\nThe system couldn't connect to core with this address:"
            msg += ' {0}'.format(settings.VIR_SERVER)
            raise ConnectionFailed(msg)

    return output


def handle_errors(error, rpc_id):
    result = {}

    if isinstance(error, ProtocolError):
        response_error = loads(history.response)
        toLog(response_error, 'debug')

        try:
            list_some_formal_error = ['ParamsError', 'GeneralError']

            for _error in list_some_formal_error:

                if _error in error.message:
                    result = {error.message[1]: (
                        error.message[0], response_error['error'].get('data'))}

                else:
                    result = response_error['error']['data']

        except KeyError:
            result = response_error

    elif isinstance(error, KeyError):
        response_error = loads(history.response)
        toLog(response_error, 'debug')

        if rpc_id == response_error['id'] and 'error' in response_error and 'fault' in response_error['error']:
            result['message'] = response_error['error'].pop('fault')
            result['code'] = response_error['error'].pop('faultCode')
            result['data'] = response_error['error'].pop('faultString')

        else:
            result['message'] = 'Client RPC Issue!'

    elif isinstance(error, socket_error):
        result['code'] = error[0]
        result['message'] = error[1]

    return result


def send_request(*args):

    return select_send_request(
        settings.CORE_HOST_SELF,
        settings.CORE_PORT_SELF,
        *args
    )


# def send_request_main(*args):

#     return select_send_request(
#         settings.CORE_HOST_MAIN,
#         settings.CORE_PORT_MAIN,
#         *args
#     )
