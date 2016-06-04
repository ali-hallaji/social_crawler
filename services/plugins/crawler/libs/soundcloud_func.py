import datetime
import soundcloud

from json import loads
from pymongo.errors import DuplicateKeyError

from config.settings import num_pages
from config.settings import page_length
from core import toLog
from core.db import cursor_soundcloud


def soundcloud_runner():
    # tuple_month_list = divide_datetime(period_years)

    client = soundcloud.Client(client_id='0f61912bac6ddba41024c18e4a7e032f')

    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    last_week = now - datetime.timedelta(days=7)
    last_month = now - datetime.timedelta(days=31)
    last_year = now - datetime.timedelta(days=365)
    ten_years = now - datetime.timedelta(days=(365 * 10))

    daily = {'from': last_day, 'to': now}
    weekly = {'from': last_week, 'to': last_day}
    monthly = {'from': last_month, 'to': last_week}
    yearly = {'from': last_year, 'to': last_month}
    ten = {'from': ten_years, 'to': last_year}

    date_list = [
        (daily, 'Daily'),
        (weekly, 'Weekly'),
        (monthly, 'Monthly'),
        (yearly, 'Yearly'),
        (ten, 'Ten years')
    ]

    for _date in date_list:
        offset = 0
        for i in range(1, num_pages + 1):
            data = client.get(
                '/tracks',
                created_at=_date[0],
                order='playback_count',
                limit=page_length,
                linked_partitioning=1,
                offset=offset
            )
            tracks = loads(data.raw_data)

            for track in tracks['collection']:
                track['created_date'] = datetime.datetime.now()

                try:
                    result = cursor_soundcloud.refined_data.insert(track)
                except DuplicateKeyError:
                    result = True
                    toLog("Duplicate Error: It can't be save record", 'error')

                if not result:
                    msg = "Crawling Error: It can't be save record"
                    msg += "{0}".format(track)
                    toLog(msg, 'error')

            offset += page_length
            toLog('{0} Crawled for soundcloud'.format(_date[1]), 'jobs')
