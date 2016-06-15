# Import Python

# Import Core
from core import toLog
from core.db import cursor_local


def get_settings(settings_type, key):
    settings = cursor_local.settings.find_one({'settings_type': settings_type})

    if settings:

        if key:
            return settings[key]

        else:
            return settings

    else:
        toLog('Get Settings: No settings in DB', 'error')


def general_settings(key=None):
    return get_settings('GeneralSettings', key)


def yt_settings(key=None):
    return get_settings('YTSettings', key)
