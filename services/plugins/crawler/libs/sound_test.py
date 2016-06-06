from json import loads
import soundcloud
import datetime

# from core.db import cursor_soundcloud
from pymongo import MongoClient

cursor_soundcloud = MongoClient('mongodb://localhost:47017')['SoundCloud']


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
        print _date[1]
        data = client.get(
            '/tracks',
            created_at=_date[0],
            order='playback_count',
            limit=200
        )
        tracks = loads(data.raw_data)

        for track in tracks:
            track['created_date'] = datetime.datetime.now()
            cursor_soundcloud.refined_data.insert(track)


soundcloud_runner()

