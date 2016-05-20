# -*- coding: utf-8 -*-
# Python Import
import bs4
import datetime
import json
import requests
import urllib
import urlparse
from twisted.internet import reactor
from apiclient.discovery import build
from pymongo.errors import DuplicateKeyError

# YouTube Crawler Import
from config.settings import DEVELOPER_KEY
from config.settings import DEVELOPER_KEY2
from config.settings import YOUTUBE_API_SERVICE_NAME
from config.settings import YOUTUBE_API_VERSION
from config.settings import period_days
from core import toLog
from core.db import cursor


def open_url_api(video_id):
    base_url = "https://www.googleapis.com/youtube/v3/videos?id="
    base_url += video_id
    base_url += "&key=" + DEVELOPER_KEY
    base_url += "&part=statistics,snippet"

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

            try:
                result = cursor.refined_data.insert(_video)

            except DuplicateKeyError:
                result = True
                toLog("Crawling Error: It can't be save record", 'error')

            if not result:
                toLog("Crawling Error: It can't be save record", 'error')

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

            try:
                result = cursor.refined_data.insert(_video)

            except DuplicateKeyError:
                result = True
                toLog("Crawling Error: It can't be save record", 'error')

            if not result:
                toLog("Crawling Error: It can't be save record", 'error')

        else:
            toLog("UnHandled Crawling: {0}".format(search_result), 'debug')

        if not result:
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

        except Exception as e:
            print e
            toLog(str(e), 'jobs')
            flag = False


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
        snippet = video.get('items', [])[0].get('snippet', {})
        statistics = video.get('items', [])[0].get('statistics', {})

        doc['thumbnails'] = snippet.get('thumbnails', '')
        doc['title'] = snippet.get('title', '')
        doc['channel_id'] = snippet.get('channelId', '')
        doc['category_id'] = snippet.get('categoryId', '')
        doc['published_at'] = snippet.get('publishedAt', '')
        doc['channel_title'] = snippet.get('channelTitle', '')
        doc['description'] = snippet.get('description', '')
        doc['keywords'] = snippet.get('tags', '')

        doc['comment_count'] = int(statistics.get('commentCount', 0))
        doc['dislikes'] = int(statistics.get('dislikeCount', 0))
        doc['favorite_count'] = int(statistics.get('favoriteCount', 0))
        doc['all_views'] = int(statistics.get('viewCount', 0))
        doc['likes'] = int(statistics.get('likeCount', 0))

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
    video_doc = cursor.refined_data.find_one({'id': _id})

    video = get_video_info(_id)

    if video:
        video['daily_views_yesterday'] = int(
            video_doc.get('daily_views_today', 0)
        )
        today_views = video['all_views'] - int(video_doc.get('all_views', 0))
        video['daily_views_today'] = today_views

        return video


def start_updating_jobs():
    less_today = datetime.datetime.now().replace(hour=0, minute=30, second=0)
    _criteria = {
        '$or': [
            {'update_video_data': {'$lte': less_today}},
            {'all_views': {'$exists': False}}
        ]
    }

    count = True
    while count:

        count = cursor.refined_data.count(_criteria)
        all_videos = cursor.refined_data.find(_criteria)

        for doc in all_videos:
            try:
                _id = doc['id']
                criteria = {'_id': doc['_id']}
                new_data = today_yesterday_data(_id)

                if not new_data:
                    continue

                _update = {'$set': new_data}
                update = cursor.refined_data.update_one(criteria, _update)

                if not update.raw_result.get('updatedExisting', None):
                    msg = "The video with this id"
                    msg += " '{0}' can't be updated".format(_id)
                    toLog(msg, 'db')

            except Exception as e:
                toLog(str(e), 'error')


def update_crawl():
    reactor.callInThread(start_updating_jobs, )
