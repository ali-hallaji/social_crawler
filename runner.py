from core.cache_control import cache_control
from core.gzip_rpc import gzip_rpc
from core.ha import ha
from core.load_balance import load_balance
from core.router import router
from core.shared_memory import shared_memory

from services.rpc_core.run_rpc import runRPC

def initRPC():
    if cache_control.key + gzip_rpc.key + ha.key + load_balance.key + router.key + shared_memory.key == 18822265971262567:
        runRPC()

