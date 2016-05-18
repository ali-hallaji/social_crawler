from services.plugins.crawler.libs import crawl_video_history


CRAWLER_LOADED_MODULE = None


def getFlag():
    global CRAWLER_LOADED_MODULE
    try:
        return CRAWLER_LOADED_MODULE
    except:
        CRAWLER_LOADED_MODULE = False
        return CRAWLER_LOADED_MODULE


def loadFlag():
    global CRAWLER_LOADED_MODULE
    CRAWLER_LOADED_MODULE = True


def unLoadFlag():
    global CRAWLER_LOADED_MODULE
    CRAWLER_LOADED_MODULE = False
