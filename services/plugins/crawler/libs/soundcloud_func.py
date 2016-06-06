import time
import datetime
import soundcloud
from dateutil import parser

from json import loads
from pymongo.errors import DuplicateKeyError

from config.settings import SOUNDCLOUD_ID
from config.settings import num_pages
from config.settings import page_length
from core import toLog
from core.db import cursor_soundcloud


def soundcloud_runner():
    client = soundcloud.Client(client_id=SOUNDCLOUD_ID)

    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    last_week = now - datetime.timedelta(days=7)
    last_month = now - datetime.timedelta(days=31)
    last_year = now - datetime.timedelta(days=365)
    ten_years = now - datetime.timedelta(days=(365 * 10))

    daily = {
        'from': last_day.strftime("%Y-%m-%d %H:%M:%S"),
        'to': now.strftime("%Y-%m-%d %H:%M:%S")
    }
    weekly = {
        'from': last_week.strftime("%Y-%m-%d %H:%M:%S"),
        'to': last_day.strftime("%Y-%m-%d %H:%M:%S")
    }
    monthly = {
        'from': last_month.strftime("%Y-%m-%d %H:%M:%S"),
        'to': last_week.strftime("%Y-%m-%d %H:%M:%S")
    }
    yearly = {
        'from': last_year.strftime("%Y-%m-%d %H:%M:%S"),
        'to': last_month.strftime("%Y-%m-%d %H:%M:%S")
    }
    ten = {
        'from': ten_years.strftime("%Y-%m-%d %H:%M:%S"),
        'to': last_year.strftime("%Y-%m-%d %H:%M:%S")
    }

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
            time.sleep(0.3)
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

                track['username'] = track.get('user', {}).get('username', '')
                track.pop('user', '')

                if 'last_modified' in track:
                    track['last_modified'] = parser.parse(
                        track['last_modified']
                    )

                if 'created_at' in track:
                    track['created_at'] = parser.parse(track['created_at'])

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


def soundcloud_update():
    all_tracks = cursor_soundcloud.refined_data.find(no_cursor_timeout=True)

    count = 1
    for track in all_tracks:
        main_track = track.copy()
        try:
            new_track = track_info(track)
            refine_track = today_yesterday_data(new_track, track)

            if not refine_track:
                toLog(
                    'Unsuccessful update: {0}'.format(main_track['id']), 'jobs'
                )
                continue

            criteria = {'_id': main_track['_id']}
            _update = {'$set': refine_track}
            update = cursor_soundcloud.refined_data.update_one(
                criteria,
                _update
            )

            if not update.raw_result.get('updatedExisting', None):
                count += 1
                msg = "The video with this id"
                msg += " '{0}' can't be updated".format(track['id'])

                if (count % 100) == 0:
                    toLog(msg, 'db')

        except Exception as e:
            count += 1

            if (count % 1000) == 0:
                toLog(str(e), 'error')


def track_info(track_doc):
    try:
        client = soundcloud.Client(client_id=SOUNDCLOUD_ID)
        track = loads(
            client.get('/tracks/{0}'.format(track_doc['id'])).raw_data
        )

        if 'last_modified' in track:
            track['last_modified'] = parser.parse(
                track['last_modified']
            )

        if 'created_at' in track:
            track['created_at'] = parser.parse(track['created_at'])

        track['username'] = track.get('user', {}).get('username', '')
        track.pop('user', '')

        track['has_yesterday'] = True
        track['update_track_data'] = datetime.datetime.now()

        return track

    except Exception as e:
        data_log = {'track_id': track_doc['id']}
        data_log['type'] = 'update_data'
        data_log['date'] = datetime.datetime.now()

        if 'list index out of range' in str(e):
            msg = "Track Id: {0} can't be fetch".format(track_doc['id'])
            data_log['reason'] = msg
            toLog(msg, 'error')

        else:
            toLog(e, 'error')

        data_log['reason'] = str(e)
        cursor_soundcloud.logs.insert(data_log)


def today_yesterday_data(track, track_doc):
    if track and ('playback_count' in track):
        track['daily_playback_count_yesterday'] = int(
            track_doc.get('daily_playback_count_today', 0)
        )
        today_playback = int(
            track['playback_count'] - int(track_doc.get('playback_count', 0))
        )
        track['daily_playback_count_today'] = today_playback

        return track


def fix_str_date():
    projection = {
        'last_modified': 1,
        'created_at': 1,
        'user.username': 1
    }
    tracks = cursor_soundcloud.refined_data.find(
        {},
        projection,
        no_cursor_timeout=True
    )

    for track in tracks:
        try:
            if 'last_modified' in track:
                track['last_modified'] = parser.parse(
                    track['last_modified']
                )

            if 'created_at' in track:
                track['created_at'] = parser.parse(track['created_at'])

        except Exception as e:
            print str(e)

        track['username'] = track.pop('user', {}).get('username', '')

        _update = {'$set': track, '$unset': {'user': ''}}
        cursor_soundcloud.refined_data.update_one(
            {'_id': track['_id']},
            _update
        )
