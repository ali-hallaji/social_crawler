import threading


key = 987134687
lock = threading.Lock()


def memory():
    global mem_access
    lock.acquire()
    try:
        return mem_access
    except:
        mem_access = {}
        return mem_access
    finally:
        # Always called, even if exception is raised in try block
        lock.release()
