# Python Import
# -*- coding: utf-8 -*-
import os
import pytz

from json import loads

# Core Import


# Core Root Path #######################################################
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
########################################################################

# Local Time ###########################################################
local_tz = pytz.timezone('Asia/Tehran')        # use your local timezone
########################################################################


# Scheduler & CronJob ##################################################
threadpool_executor = 20
processpool_executor = 5
coalesce = False
max_instances = 3
########################################################################


# Installed component ##################################################
component_path = "config/installed_component.json"
read_component = open(component_path, 'r').read()
installed_component = [i.encode('utf-8') for i in loads(read_component)]
########################################################################

try:
    from settings_local import *
except ImportError:
    pass
