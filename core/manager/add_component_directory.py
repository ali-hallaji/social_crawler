# Python Import
import os

# Core import
from config.settings import BASE_DIR


def mkdir(plugin):
    path = BASE_DIR + '/services/plugins/' + plugin

    if not os.path.exists(path):
        os.makedirs(path)
