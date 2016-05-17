# Python import

# Core import
from config.settings import BASE_DIR


def make_init(plugin, address):
    path = BASE_DIR + '/core/manager/init.txt'
    init = open(path, 'r').read().format(*([plugin.upper(), ]*9))
    make = open(address, 'w')
    make.write(init)
    make.close()
