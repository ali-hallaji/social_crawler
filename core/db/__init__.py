from mongo_drivers import MongoConnectionGlobal
from mongo_drivers import MongoConnectionLocal
from mongo_drivers import MongoConnectionSelf


def MongoCursorDefsLocal(db):
    return MongoConnectionLocal().getCursor(db)


def MongoCursorDefsSelf(db):
    return MongoConnectionSelf().getCursor(db)


def MongoCursorDefsGlobal(db):
    return MongoConnectionGlobal().getCursor(db)


cursor_local = MongoCursorDefsLocal('Youtube')
cursor_global = MongoCursorDefsGlobal('Youtube')
cursor = MongoCursorDefsSelf('Youtube')
