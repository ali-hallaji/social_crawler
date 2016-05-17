from threading import Thread
from twisted.internet import reactor
from twisted.web import server

from config.settings import CORE_PORT
from config.settings import background_process_thread_pool as pool
from services.rpc_core.main_json_rpc import CoreServices


def runRPC():
    print 'Core Services running  \t\t\t\t\t\t[OK]'
    Thread(target=run_reactor).start()


def run_reactor():
    init = CoreServices()
    reactor.listenTCP(CORE_PORT, server.Site(init))
    reactor.suggestThreadPoolSize(pool)
    reactor.run(installSignalHandlers=False)
