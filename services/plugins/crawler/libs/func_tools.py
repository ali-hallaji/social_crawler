# Python Import
import datetime

from apiclient.discovery import build

# YouTube Crawler Import
from config.settings import DEVELOPER_KEY
from config.settings import YOUTUBE_API_SERVICE_NAME
from config.settings import YOUTUBE_API_VERSION
from config.settings import period_days
from core import toLog
from core.db import cursor
from core.patterns.class_singleton import singleton


@singleton
def build_youtube_api():
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY
    )

    return youtube


def executor_crawl(_to, _from, criteria, next_page_token=None):
    msg = 'Start executer:---> start: {0} | end: {1}'.format(_from, _to)
    msg += " criteria: {0} | next_page: {1}".format(criteria, next_page_token)
    toLog(msg, 'jobs')

    youtube = build_youtube_api()

    # Call the search.list method to retrieve results matching the specified
    # query term.
    if next_page_token:
        search_response = youtube.search().list(
            q=criteria['q'],
            maxResults=criteria['max_results'],
            part="id,snippet",
            type='video',
            order='viewCount',
            pageToken=next_page_token,
            videoCategoryId='10',  # Music & Entertaiment Category
            publishedAfter=_from.strftime('%Y-%m-%dT%H:%M:%SZ'),
            publishedBefore=_to.strftime('%Y-%m-%dT%H:%M:%SZ'),
        ).execute()

    else:
        search_response = youtube.search().list(
            q=criteria['q'],
            maxResults=criteria['max_results'],
            part="id,snippet",
            type='video',
            order='viewCount',
            videoCategoryId='10',  # Music & Entertaiment Category
            publishedAfter=_from.strftime('%Y-%m-%dT%H:%M:%SZ'),
            publishedBefore=_to.strftime('%Y-%m-%dT%H:%M:%SZ'),
        ).execute()

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        _video = {'created_date': datetime.datetime.now()}
        update = None

        if search_result["kind"] == "youtube#video":
            _video['href'] = 'https://www.youtube.com/watch?v='
            _video['img'] = search_result['snippet']['thumbnails']['default']
            _video['title'] = search_result['snippet']['title']
            _video['channel_id'] = search_result['snippet']['channelId']
            _video['channel_title'] = search_result['snippet']['channelTitle']
            _video['published_at'] = search_result['snippet']['publishedAt']
            _video['description'] = search_result['snippet']['description']

            if 'id' in search_result['snippet']:
                _video['href'] += search_result['snippet']['id']['videoId']
                _video['id'] = search_result['snippet']['id']['videoId']

            else:
                _video['href'] += search_result['id']['videoId']
                _video['id'] = search_result['id']['videoId']

            _criteria = {'id': {'$ne': _video['id']}}
            _update = {'$set': _video}
            update = cursor.refined_data.update_one(
                _criteria,
                _update,
                upsert=True
            )

        elif search_result["kind"] == "youtube#searchResult":
            _video['href'] = 'https://www.youtube.com/watch?v='
            _video['img'] = search_result['snippet']['thumbnails']['default']
            _video['title'] = search_result['snippet']['title']
            _video['channel_id'] = search_result['snippet']['channelId']
            _video['channel_title'] = search_result['snippet']['channelTitle']
            _video['published_at'] = search_result['snippet']['publishedAt']
            _video['description'] = search_result['snippet']['description']

            if 'id' in search_result['snippet']:
                _video['href'] += search_result['snippet']['id']['videoId']
                _video['id'] = search_result['snippet']['id']['videoId']

            else:
                _video['href'] += search_result['id']['videoId']
                _video['id'] = search_result['id']['videoId']

            _criteria = {'id': {'$ne': _video['id']}}
            _update = {'$set': _video}
            update = cursor.refined_data.update_one(
                _criteria,
                _update,
                upsert=True
            )

        else:
            toLog("UnHandled Crawling: {0}".format(search_result), 'debug')

        if not update.raw_result['updatedExisting']:
            toLog("Crawling Error: It can't be save record", 'error')

    # Create Next Page
    next_page_token = search_response.get("nextPageToken")

    msg = 'End executer:---> start: {0} | end: {1}'.format(_from, _to)
    msg += " criteria: {0} | next_page: {1}".format(criteria, next_page_token)
    toLog(msg, 'jobs')

    return next_page_token


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


def execute_batch(_from, _to, criteria):

    flag = True
    next_page = None

    while flag:

        try:
            next_page = executor_crawl(_to, _from, criteria, next_page)

        except:
            flag = False
