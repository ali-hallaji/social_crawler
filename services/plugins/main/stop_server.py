# python import

# Core Services import
from core.generals.scheduler import scheduler
from services.libs.register import register
from services.libs.async_call import asynchronous


@register
class StopServer:
    """
        Stop Server
    """
    __name__ = 'stop'
    __namespace__ = 'MainComponent'
    __full_name__ = 'main.stop'
    documentation = """
        This is method for shutdown your Auth service.

        e.g:
        main.stop() > True


        Keyword arguments:


        ACL:
            TODO:
    """

    @asynchronous
    def run(self):
        from twisted.internet import reactor
        print "Core Services shutdown       \t\t\t\t\t   [OK]"

        print scheduler.print_jobs(out=None)
        scheduler.shutdown(
            wait=False,
            close_jobstores=True
        )
        reactor.callFromThread(reactor.stop)

StopServer()
