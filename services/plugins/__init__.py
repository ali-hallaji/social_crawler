from config.settings import installed_component
from core import toLog
__all__ = installed_component


try:
    # because we want to import using a variable, do it this way
    # create a global object containging our component
    import_component = __import__('services.plugins.', fromlist=["*"])
    globals()['services.plugins.'] = import_component

except ImportError as e:
    error = "{}".format(e)
    toLog(error, 'error')
