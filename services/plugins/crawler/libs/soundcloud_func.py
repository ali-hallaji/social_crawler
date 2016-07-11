import datetime
import os
import requests
import socket
import time
import subprocess

from twisted.internet import reactor

from dateutil import parser
from pymongo.errors import DuplicateKeyError

from config.settings import SOUNDCLOUD_ID
from config.settings import SSH_ADDRESS
from config.settings import SSH_PASS
from config.settings import SSH_USER
from config.settings import num_pages
from config.settings import page_length

from core import toLog
from core.db import cursor_soundcloud
# from services.libs.async_call import asynchronous_background
from services.plugins.crawler.libs.migrate_to_mysql import sc_most_played


# @asynchronous_background
def ssh_connection():
    cmd = "sshpass -p '{0}' ssh -D 9153  {1}@{2}".format(
        SSH_PASS,
        SSH_USER,
        SSH_ADDRESS
    )
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    # t = os.system(cmd)
    # print 'Done SSH %s' % t


def spoofing():
    real_create_conn = socket.create_connection

    def set_src_addr(*args):
        address, timeout = args[0], args[1]
        source_address = ('201.X.X.1', 0)
        return real_create_conn(address, timeout, source_address)

    socket.create_connection = set_src_addr


def soundcloud_runner():
    toLog("Start crawling soundcloud ", 'jobs')
    # client = soundcloud.Client(client_id=SOUNDCLOUD_ID)

    # now = datetime.datetime.now()
    # last_day = now - datetime.timedelta(days=1)
    # last_week = now - datetime.timedelta(days=7)
    # last_month = now - datetime.timedelta(days=31)
    # last_year = now - datetime.timedelta(days=365)
    # ten_years = now - datetime.timedelta(days=(365 * 10))

    # daily = {
    #     'from': last_day.strftime("%Y-%m-%d %H:%M:%S"),
    #     'to': now.strftime("%Y-%m-%d %H:%M:%S")
    # }
    # weekly = {
    #     'from': last_week.strftime("%Y-%m-%d %H:%M:%S"),
    #     'to': last_day.strftime("%Y-%m-%d %H:%M:%S")
    # }
    # monthly = {
    #     'from': last_month.strftime("%Y-%m-%d %H:%M:%S"),
    #     'to': last_week.strftime("%Y-%m-%d %H:%M:%S")
    # }
    # yearly = {
    #     'from': last_year.strftime("%Y-%m-%d %H:%M:%S"),
    #     'to': last_month.strftime("%Y-%m-%d %H:%M:%S")
    # }
    # ten = {
    #     'from': ten_years.strftime("%Y-%m-%d %H:%M:%S"),
    #     'to': last_year.strftime("%Y-%m-%d %H:%M:%S")
    # }

    # date_list = [
    #     (daily, 'Daily'),
    #     (weekly, 'Weekly'),
    #     (monthly, 'Monthly'),
    #     (yearly, 'Yearly'),
    #     (ten, 'Ten years')
    # ]

    kind_list = [
        'top',      # Top 50
        'trending'  # New & Hot
    ]

    genres_list = [
        "all-music",
        "all-audio",
        "alternativerock",
        "ambient",
        "classical",
        "country",
        "danceedm",
        "dancehall",
        "deephouse",
        "disco",
        "drumbass",
        "dubstep",
        "electronic",
        "folksingersongwriter",
        "hiphoprap",
        "house",
        "indie",
        "jazzblues",
        "latin",
        "metal",
        "piano",
        "pop",
        "rbsoul",
        "reggae",
        "reggaeton",
        "rock",
        "soundtrack",
        "techno",
        "trance",
        "trap",
        "triphop",
        "world",
        "audiobooks",
        "business",
        "comedy",
        "entertainment",
        "learning",
        "newspolitics",
        "religionspirituality",
        "science",
        "sports",
        "storytelling",
        "technology",
    ]

    proxies = {
        'http': 'socks5://localhost:9153',
        'https': 'socks5://localhost:9153'
    }
    headers = {
        'User-Agent': 'Maryam&Ali'
    }
    reactor.callInThread(ssh_connection,)

    for kind in kind_list:
        for genre in genres_list:
            offset = 0
            for i in range(1, num_pages + 1):
                url = "https://api-v2.soundcloud.com"
                url += "/charts?kind={0}".format(kind)
                url += "&genre=soundcloud:genres:{0}&client".format(genre)
                url += "_id={0}&offset={1}&".format(SOUNDCLOUD_ID, offset)
                url += "limit={0}&linked_partitioning=1".format(page_length)
                time.sleep(0.15)
                data = requests.get(url, headers=headers, proxies=proxies)

                try:
                    loads_data = data.json()

                    if loads_data and 'error' not in loads_data:
                        catharsis(loads_data)
                    else:
                        pass

                except Exception as e:
                    print str(e)

                offset += page_length

    toLog("End crawling soundcloud ", 'jobs')

    # for _date in date_list:
    #     offset = 0
    #     for i in range(1, num_pages + 1):
    #         data = client.get(
    #             '/tracks',
    #             created_at=_date[0],
    #             order='playback_count',
    #             limit=page_length,
    #             linked_partitioning=1,
    #             offset=offset
    #         )

    #         catharsis(loads(data.raw_data))

    #         offset += page_length
    #         toLog('{0} Crawled for soundcloud'.format(_date[1]), 'jobs')


def soundcloud_update():
    toLog("Start updating soundcloud ", 'jobs')
    less_today = datetime.datetime.now().replace(hour=2, minute=30, second=0)
    _criteria = {
        '$or': [
            {'update_track_data': {'$lte': less_today}},
            {'update_track_data': {'$exists': False}}
        ]
    }
    projection = {
        'id': 1
    }
    all_tracks = cursor_soundcloud.refined_data.find(
        _criteria,
        projection,
        no_cursor_timeout=True
    )

    count = 1
    print all_tracks.count()
    print datetime.datetime.now()
    reactor.callInThread(ssh_connection,)

    for track in all_tracks:
        time.sleep(0.15)
        try:
            new_track = track_info(track)
            refine_track = today_yesterday_data(new_track, track)

            if not refine_track:
                toLog(
                    'Unsuccessful update: {0}'.format(track['id']), 'jobs'
                )
                continue

            criteria = {'_id': track['_id']}
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

    toLog("End updating soundcloud ", 'jobs')
    sc_most_played()


def track_info(track_doc):
    proxies = {
        'http': 'socks5://localhost:9153',
        'https': 'socks5://localhost:9153'
    }
    headers = {
        'User-Agent': 'Maryam&Ali'
    }
    try:
        url = "https://api-v2.soundcloud.com/tracks/" + str(track_doc['id'])
        url += "?client_id=" + SOUNDCLOUD_ID
        track = requests.get(url, headers=headers, proxies=proxies)
        track = track.json()

        if 'last_modified' in track:
            track['last_modified'] = parser.parse(
                track['last_modified']
            )

        if 'created_at' in track:
            track['created_at'] = parser.parse(track['created_at'])

        if 'user' in track:
            if 'username' in track['user']:
                track['username'] = track['user']['username']

            del track['user']

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


def today_yesterday_data(track, _id):
    # This is good
    criteria = {'_id': _id['_id']}
    projection = {
        'playback_count': 1,
        'daily_playback_count_today': 1
    }
    track_doc = cursor_soundcloud.refined_data.find_one(criteria, projection)

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

        if 'last_modified' in track:
            track['last_modified'] = parser.parse(
                str(track['last_modified'])
            )

        if 'created_at' in track:
            track['created_at'] = parser.parse(str(track['created_at']))

        if 'user' in track:
            if 'username' in track['user']:
                track['username'] = track['user']['username']

            del track['user']

        _update = {'$set': track, '$unset': {'user': ''}}
        cursor_soundcloud.refined_data.update_one(
            {'_id': track['_id']},
            _update
        )


def pre_catharsis(track):
    new_track = {}

    if 'track' in track:
        for k, v in track['track'].items():
            new_track[k] = v

        new_track['score'] = track['score']
        return new_track

    else:
        return track


def catharsis(tracks):
    counter = 0
    for track in tracks['collection']:
        track = pre_catharsis(track)
        track['created_date'] = datetime.datetime.now()

        if not track.get('isrc', None):
            if track.get('publisher_metadata', None):
                track['isrc'] = track["publisher_metadata"].get("isrc", None)

        if 'user' in track:
            if 'username' in track['user']:
                track['username'] = track['user']['username']

            del track['user']

        if 'last_modified' in track:
            track['last_modified'] = parser.parse(
                track['last_modified']
            )

        if 'created_at' in track:
            track['created_at'] = parser.parse(track['created_at'])

        try:
            result = cursor_soundcloud.refined_data.insert(track)

        except DuplicateKeyError:
            counter += 1
            result = True

            if (counter % 25) == 0:
                toLog("Duplicate Error: It can't be save record", 'error')

        if not result:
            msg = "Crawling Error: It can't be save record"
            msg += "{0}".format(track)
            toLog(msg, 'error')
