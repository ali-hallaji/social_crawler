# Python Import


# Core import
from create_init_file import make_init
from config.settings import BASE_DIR


def execute_assign(plugin):
    init_file = BASE_DIR + '/services/plugins/' + plugin + '/__init__.py'
    make_init(plugin, init_file)

