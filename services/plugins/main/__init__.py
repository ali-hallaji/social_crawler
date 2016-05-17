MAIN_LOADED_MODULE = None


def getFlag():
    global MAIN_LOADED_MODULE
    try:
        return MAIN_LOADED_MODULE
    except:
        MAIN_LOADED_MODULE = False
        return MAIN_LOADED_MODULE


def loadFlag():
    global MAIN_LOADED_MODULE
    MAIN_LOADED_MODULE = True


def unLoadFlag():
    global MAIN_LOADED_MODULE
    MAIN_LOADED_MODULE = False
