# -*- coding: utf-8 -*-
# Python Import
import bs4
import datetime
import json
import requests
import time
import urllib
import urlparse

from dateutil import parser

from apiclient.discovery import build
from pymongo.errors import DuplicateKeyError

# YouTube Crawler Import
from config.settings import DEVELOPER_KEY
from config.settings import DEVELOPER_KEY2
from config.settings import YOUTUBE_API_SERVICE_NAME
from config.settings import YOUTUBE_API_VERSION
from config.settings import batch_loop
from config.settings import delete_month
from config.settings import delete_video_count
from config.settings import period_days
from core import toLog
from core.db import cursor
from services.plugins.crawler.libs.migrate_to_mysql import yt_mosted_viewed
from services.plugins.crawler.libs.soundcloud_func import soundcloud_runner
from services.plugins.crawler.libs.soundcloud_func import soundcloud_update


def create_base_url(video_id, api_key):
    base_url = "https://www.googleapis.com/youtube/v3/videos?id="
    base_url += video_id
    base_url += "&key=" + api_key
    base_url += "&part=statistics,snippet"

    return base_url


def open_url_api(video_id):
    base_url = create_base_url(video_id, DEVELOPER_KEY)
    response = urllib.urlopen(base_url).read()
    data = json.loads(response)

    if ('error' in data) and data['error']['code'] == 403:
        base_url = create_base_url(video_id, DEVELOPER_KEY2)
        response = urllib.urlopen(base_url).read()
        data = json.loads(response)

    return data


def build_youtube_api():
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY
    )

    return youtube


def divide_datetime(period_years):
    now = datetime.datetime.now()
    last = now - datetime.timedelta(days=period_years * 365)

    all_months = period_years * 12
    month_list = [now]
    tuple_month_list = []

    for month in range(1, all_months + 1):
        new = now - datetime.timedelta(days=month * period_days)
        tuple_month_list.append((month_list[-1], new))
        month_list.append(new)

    tuple_month_list.append((month_list[-1], last))

    return tuple_month_list


def crawl_search(keyword, page):
    if ' ' in keyword:
        keyword = keyword.replace(' ', '+')

    url = 'https://www.youtube.com/results?search_sort=video_view_count'
    # url += '&filters=today'
    url += '&search_query=' + keyword
    url += '&page={0}'.format(page)

    text = requests.get(url).text
    soup = bs4.BeautifulSoup(text, "html.parser")

    div = []

    for d in soup.find_all('div'):
        if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']:
            div.append(d)

    for d in div:
        doc = {'created_date': datetime.datetime.now()}
        img0 = d.find_all('img')[0]
        a0 = d.find_all('a')[0]

        if not img0.has_attr('data-tumb'):
            doc['img'] = img0['src']

        else:
            doc['img'] = img0['data-tumb']

        a0 = [x for x in d.find_all('a') if x.has_attr('title')][0]
        doc['title'] = a0['title']
        doc['href'] = 'https://www.youtube.com' + a0['href']
        doc['id'] = get_video_id(doc['href'])

        try:
            result = cursor.refined_data.insert(doc)

        except DuplicateKeyError:
            result = True
            toLog("Crawling Error: It can't be save record", 'error')

        if not result:
            toLog("Crawling Error: It can't be save record", 'error')


def get_video_id(url):
    url_data = urlparse.urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    video = query["v"][0]
    return video


def get_video_info(video_id):
    doc = {}

    try:
        video = open_url_api(video_id)

        if 'items' in video:
            if video['items'] == []:
                doc['private'] = True
                doc['update_video_data'] = datetime.datetime.now()

                return doc

        snippet = video.get('items', [])[0].get('snippet', {})
        statistics = video.get('items', [])[0].get('statistics', {})

        doc['thumbnails'] = snippet.get('thumbnails', '')
        doc['title'] = snippet.get('title', '')
        doc['channel_id'] = snippet.get('channelId', '')
        doc['category_id'] = snippet.get('categoryId', '')
        doc['published_at'] = parser.parse(snippet.get('publishedAt', ''))
        doc['channel_title'] = snippet.get('channelTitle', '')
        doc['description'] = snippet.get('description', '')
        doc['keywords'] = snippet.get('tags', '')

        doc['comment_count'] = int(statistics.get('commentCount', 0))
        doc['dislikes'] = int(statistics.get('dislikeCount', 0))
        doc['favorite_count'] = int(statistics.get('favoriteCount', 0))
        doc['all_views'] = int(statistics.get('viewCount', 0))
        doc['likes'] = int(statistics.get('likeCount', 0))

        if '-' in doc.get('title', ''):
            splited = doc['title'].split(' - ')
            doc['artist'] = splited[0].strip()
            doc['song_title'] = ' - '.join(splited[1:])
            doc['song_title'] = doc['song_title'].strip()

        else:
            doc['artist'] = doc.get('title', '')
            doc['song_title'] = doc.get('title', '')

        doc['has_yesterday'] = True
        doc['update_video_data'] = datetime.datetime.now()

        return doc

    except Exception as e:
        data_log = {'video_id': video_id}
        data_log['type'] = 'update_data'
        data_log['date'] = datetime.datetime.now()

        if 'list index out of range' in str(e):
            msg = "Video Id: {0} can't be fetch".format(video_id)
            data_log['reason'] = msg
            toLog(msg, 'error')

        else:
            toLog(e, 'error')

        data_log['reason'] = str(e)
        cursor.logs.insert(data_log)


def today_yesterday_data(_id):
    video_doc = cursor.refined_data.find_one(
        {
            'id': _id,
            'private': {
                '$ne': True
            }
        }
    )
    video = get_video_info(_id)

    if video and ('all_views' in video):
        video['daily_views_yesterday'] = int(
            video_doc.get('daily_views_today', 0)
        )
        today_views = video['all_views'] - int(video_doc.get('all_views', 0))
        video['daily_views_today'] = today_views

        return video


def start_updating_jobs():
    less_today = datetime.datetime.now().replace(hour=4, minute=30, second=0)
    _criteria = {
        'private': {'$ne': True},
        '$or': [
            {'update_video_data': {'$lte': less_today}},
            {'all_views': {'$exists': False}}
        ]
    }
    _projection = {
        'id': 1
    }
    toLog('Start updating jobs criteria: {0}'.format(str(_criteria)), 'jobs')

    all_videos = cursor.refined_data.find(
        _criteria,
        _projection,
        no_cursor_timeout=True
    )

    for doc in all_videos:
        try:
            _id = doc['id']
            criteria = {'_id': doc['_id']}
            new_data = today_yesterday_data(_id)

            if not new_data:
                # toLog('Unsuccessful update: {0}'.format(_id), 'jobs')
                continue

            _update = {'$set': new_data}
            update = cursor.refined_data.update_one(criteria, _update)

            if not update.raw_result.get('updatedExisting', None):
                msg = "The video with this id"
                msg += " '{0}' can't be updated".format(_id)
                toLog(msg, 'db')

        except Exception as e:
            toLog(str(e), 'error')

    toLog("Start updating soundcloud ", 'jobs')
    soundcloud_update()
    toLog("End updating soundcloud ", 'jobs')
    clean_title()
    yt_mosted_viewed()


def execute_batch(_date, name, criteria):
    next_page = None

    for i in range(1, (batch_loop + 1)):
        try:
            time.sleep(0.5)
            next_page = executor_crawl(_date, name, criteria, next_page)

        except Exception as e:
            toLog(str(e), 'error')


def bulk_jobs_from_dates():
    # tuple_month_list = divide_datetime(period_years)

    now = datetime.datetime.now()
    last_day = now - datetime.timedelta(days=1)
    last_week = now - datetime.timedelta(days=7)
    last_month = now - datetime.timedelta(days=31)
    last_year = now - datetime.timedelta(days=365)
    ten_years = now - datetime.timedelta(days=(365 * 10))

    weekly = (last_week, last_day)
    monthly = (last_month, last_week)
    yearly = (last_year, last_month)
    ten = (ten_years, last_year)

    date_list = [
        ((last_day, "Now"), 'Daily'),
        (weekly, 'Weekly'),
        (monthly, 'Monthly'),
        (yearly, 'Yearly'),
        (ten, 'Ten years')
    ]
    category_list = ['10', '24']
    order_list = ['date', 'rating', 'relevance', 'viewCount']

    for order in order_list:
        for _date, _name in date_list:
            for item in category_list:
                criteria = {
                    'max_results': 50,
                    'q': '',
                    'category_id': item,
                    'order': order
                }
                result = execute_batch(_date, _name, criteria)

                msg = _name + " Crawler Jobs"
                msg += " from: {0} | category: {1}".format(_date, item)
                msg += "{0}".format(str(result))
                toLog(msg, 'jobs')

    toLog("Start crawling soundcloud ", 'jobs')
    soundcloud_runner()
    toLog("End crawling soundcloud ", 'jobs')
    delete_video()


def executor_crawl(_date, name, criteria, next_page_token=None):
    youtube = build_youtube_api()
    # Call the search.list method to retrieve results matching the specified
    # query term.
    if name == 'Daily':
        if next_page_token:
            search_response = youtube.search().list(
                q=criteria['q'],
                maxResults=criteria['max_results'],
                part="id,snippet",
                type='video',
                order=criteria['order'],
                pageToken=next_page_token,
                videoCategoryId=criteria['category_id'],  # Music/Entertaiment
                publishedAfter=_date[0].strftime('%Y-%m-%dT%H:%M:%SZ'),
                # publishedBefore=_to.strftime('%Y-%m-%dT%H:%M:%SZ'),
            ).execute()

        else:
            search_response = youtube.search().list(
                q=criteria['q'],
                maxResults=criteria['max_results'],
                part="id,snippet",
                type='video',
                order=criteria['order'],
                videoCategoryId=criteria['category_id'],  # Music/Entertaiment
                publishedAfter=_date[0].strftime('%Y-%m-%dT%H:%M:%SZ'),
                # publishedBefore=_to.strftime('%Y-%m-%dT%H:%M:%SZ'),
            ).execute()

    else:
        if next_page_token:
            search_response = youtube.search().list(
                q=criteria['q'],
                maxResults=criteria['max_results'],
                part="id,snippet",
                type='video',
                order=criteria['order'],
                pageToken=next_page_token,
                videoCategoryId=criteria['category_id'],  # Music/Entertaiment
                publishedAfter=_date[0].strftime('%Y-%m-%dT%H:%M:%SZ'),
                publishedBefore=_date[1].strftime('%Y-%m-%dT%H:%M:%SZ'),
            ).execute()

        else:
            search_response = youtube.search().list(
                q=criteria['q'],
                maxResults=criteria['max_results'],
                part="id,snippet",
                type='video',
                order=criteria['order'],
                videoCategoryId=criteria['category_id'],  # Music/Entertaiment
                publishedAfter=_date[0].strftime('%Y-%m-%dT%H:%M:%SZ'),
                publishedBefore=_date[1].strftime('%Y-%m-%dT%H:%M:%SZ'),
            ).execute()

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    duplicate = 0

    for search_result in search_response.get("items", []):
        _video = {'created_date': datetime.datetime.now()}

        category_trans = {'24': 'Entertainment', '10': 'Music'}
        _video['category_name'] = category_trans.get(
            criteria['category_id'],
            'UnKnown'
        )

        if search_result["kind"] == "youtube#video":
            _publish = parser.parse(search_result['snippet']['publishedAt'])
            _video['href'] = 'https://www.youtube.com/watch?v='
            _video['img'] = search_result['snippet']['thumbnails']['default']
            _video['title'] = search_result['snippet']['title']
            _video['channel_id'] = search_result['snippet']['channelId']
            _video['channel_title'] = search_result['snippet']['channelTitle']
            _video['published_at'] = _publish
            _video['description'] = search_result['snippet']['description']

            if 'id' in search_result['snippet']:
                _video['href'] += search_result['snippet']['id']['videoId']
                _video['id'] = search_result['snippet']['id']['videoId']
            else:
                _video['href'] += search_result['id']['videoId']
                _video['id'] = search_result['id']['videoId']

            try:
                result = cursor.refined_data.insert(_video)
            except DuplicateKeyError:
                result = True
                if (duplicate % 1000) == 0:
                    toLog("Duplicate Error: 1000 records", 'error')

                duplicate += 1

            if not result:
                msg = "Crawling Error: It can't be save record"
                msg += "{0}".format(search_result)
                toLog(msg, 'error')

        elif search_result["kind"] == "youtube#searchResult":
            _publish = parser.parse(search_result['snippet']['publishedAt'])
            _video['href'] = 'https://www.youtube.com/watch?v='
            _video['img'] = search_result['snippet']['thumbnails']['default']
            _video['title'] = search_result['snippet']['title']
            _video['channel_id'] = search_result['snippet']['channelId']
            _video['channel_title'] = search_result['snippet']['channelTitle']
            _video['published_at'] = _publish
            _video['description'] = search_result['snippet']['description']

            if 'id' in search_result['snippet']:
                _video['href'] += search_result['snippet']['id']['videoId']
                _video['id'] = search_result['snippet']['id']['videoId']
            else:
                _video['href'] += search_result['id']['videoId']
                _video['id'] = search_result['id']['videoId']

            try:
                result = cursor.refined_data.insert(_video)
            except DuplicateKeyError:
                result = True
                if (duplicate % 1000) == 0:
                    toLog("Duplicate Error: 1000 records", 'error')

                duplicate += 1

            if not result:
                msg = "Crawling Error: It can't be save record"
                msg += "{0}".format(search_result)
                toLog(msg, 'error')

        else:
            toLog("UnHandled Crawling: {0}".format(search_result), 'debug')

        if not result:
            toLog("Crawling Error: It can't be save record", 'error')

    # Create Next Page
    next_page_token = search_response.get("nextPageToken")
    return next_page_token


def clean_title():
    projection = {'title': 1}
    videos = cursor.refined_data.find({}, projection, no_cursor_timeout=True)

    for video in videos:
        if '-' in video['title']:
            splited = video['title'].split(' - ')
            video['artist'] = splited[0].strip()
            video['song_title'] = ' - '.join(splited[1:])
            video['song_title'] = video['song_title'].strip()

        else:
            video['artist'] = video.get('title', '')
            video['song_title'] = video.get('title', '')

        _update = {'$set': video}
        cursor.refined_data.update_one({'_id': video['_id']}, _update)


def clean_category_name():
    projection = {'category_id': 1}
    videos = cursor.refined_data.find({}, projection, no_cursor_timeout=True)
    category_trans = {'24': 'Entertainment', '10': 'Music'}

    for video in videos:
        if video.get('category_id', None):
            video['category_name'] = category_trans.get(
                video['category_id'],
                'UnKnown'
            )

        _update = {'$set': video}
        cursor.refined_data.update_one({'_id': video['_id']}, _update)


def delete_video():
    now = datetime.datetime.now()
    last_six_month = now - datetime.timedelta(days=31 * delete_month)

    criteria = {
        'published_at': {'$lte': last_six_month},
        'all_views': {'$lte': delete_video_count}
    }
    delete = cursor.refined_data.remove(criteria)

    toLog('Removed "{0}" videos from DB'.format(str(delete)), 'debug')
