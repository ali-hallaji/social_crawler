import re
import datetime

def email_validator(email):
    pattern = re.compile('^[a-zA-Z0-9._]+\\@[a-zA-Z0-9._]+\\.[a-zA-Z]{3,}$')
    check_mail = re.match(pattern, email)
    if check_mail:
        return True
    else:
        return False


def url_validator(url):
    pattern = re.compile('^https?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+[A-Z]{2,6}\\.?|localhost|\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})(?::\\d+)?(?:/?|[/?]\\S+)$', re.IGNORECASE)
    check_url = re.match(pattern, url)
    if check_url:
        return True
    else:
        return False


def date_validator(_date):
    _date = _date.replace('-', '/')
    pattern = '%Y/%m/%d'
    try:
        return datetime.datetime.strptime(_date, pattern).date()
    except ValueError:
        return False


def datetime_validator(_datetime):
    _datetime = _datetime.replace('-', '/')
    _datetime = _datetime.replace(',', ':')
    pattern = '%Y/%m/%d %H:%M:%S'
    try:
        return datetime.datetime.strptime(_datetime, pattern)
    except ValueError:
        return False


def time_validator(_time):
    _time = _time.replace(',', ':')
    pattern = '%H:%M:%S'
    try:
        return datetime.datetime.strptime(_time, pattern).time()
    except ValueError:
        return False


def epoch_datetime(_datetime):
    if isinstance(_datetime, (float, basestring)):
        dt = datetime.datetime.fromtimestamp(_datetime)
        return dt
    raise Exception('Wrong Type!')


def compute_timedelta(value):
    if isinstance(value, datetime.date):
        td = value - datetime.datetime(1970, 1, 1, 0, 0, 0)
        return td
    raise Exception('Wrong Type!')


def bool_validator(boolean):
    dict_bool = {'1': True,
     '0': False,
     'false': False,
     'true': True}
    try:
        return {'result': dict_bool[str(boolean)]}
    except KeyError:
        return False
