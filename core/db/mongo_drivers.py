import urllib

from pymongo import MongoClient
from pymongo import ReadPreference

from config import settings
from core.patterns.class_singleton import Singleton


@Singleton
class MongoConnectionGlobal(object):
    __db = None

    @classmethod
    def get_connection(cls):
        """Singleton method for running Mongo instance"""
        if cls.__db is None:
            user = getattr(settings, 'GLOBAL_MONGO_USER', None)
            password = getattr(settings, 'GLOBAL_MONGO_PASSWORD', None)

            if user and password:
                password = urllib.quote_plus(password)
                auth = '{0}:{1}@'.format(user, password)
            else:
                auth = ''

            if getattr(settings, 'BALANCING', None):
                address = settings.MONGO_LOAD_BALANCE
            else:
                address = '{0}:{1}'.format(
                    settings.MONGO_HOST_GLOBAL,
                    settings.MONGO_PORT_GLOBAL
                )

            connection_string = 'mongodb://{}{}'.format(auth, address)

            cls.__db = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=6000, maxPoolSize=None,
                read_preference=ReadPreference.NEAREST, connect=False
            )
        return cls.__db

    def __init__(self):
        self.get_connection()

    def getCursor(self, db):
        return self.__db[db]


@Singleton
class MongoConnectionLocal(object):
    __db = None

    @classmethod
    def get_connection(cls):
        """Singleton method for running Mongo instance"""
        if cls.__db is None:
            cls.__db = MongoClient(
                host=settings.MONGO_HOST_LOCAL, port=settings.MONGO_PORT_LOCAL,
                maxPoolSize=None, connect=False
            )
        return cls.__db

    def __init__(self):
        self.get_connection()

    def getCursor(self, db):
        return self.__db[db]


@Singleton
class MongoConnectionSelf(object):
    __db = None

    @classmethod
    def get_connection(cls):
        """Singleton method for running Mongo instance"""
        if cls.__db is None:
            cls.__db = MongoClient(
                host=settings.MONGO_HOST_SELF, port=settings.MONGO_PORT_SELF,
                maxPoolSize=None, connect=False
            )
        return cls.__db

    def __init__(self):
        self.get_connection()

    def getCursor(self, db):
        return self.__db[db]
