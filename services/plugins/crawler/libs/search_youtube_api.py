#!/usr/bin/python
import datetime
from pprint import pprint

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyD9O5FIwU3V1teLw0UcssN8TxL7Zl15erA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(options):

    # set time for last 24 hrs ago
    now = datetime.datetime.now()
    last = now - datetime.timedelta(hours=24)

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY
    )

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=options.q,
        maxResults=options.max_results,
        part="id,snippet",
        type='video',
        order='viewCount',
        videoCategoryId='10',  # This category belong to Music & Entertaiment
        publishedAfter=last.strftime('%Y-%m-%dT%H:%M:%SZ'),
        publishedBefore=now.strftime('%Y-%m-%dT%H:%M:%SZ'),
    ).execute()

    videos = []
    channels = []
    playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        _video = {}
        channel = {}
        playlist = {}

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

            videos.append(_video)

        elif search_result["kind"] == "youtube#channel":
            channel['title'] = search_result["snippet"]["title"]
            channel['href'] = 'https://www.youtube.com/channel?v='
            channel['href'] += search_result["id"]["channelId"]
            channel['id'] = search_result["id"]["channelId"]
            channels.append(channel)

        elif search_result["kind"] == "youtube#playlist":
            playlist['title'] = search_result["snippet"]["title"]
            playlist['href'] = 'https://www.youtube.com/playlist?v='
            playlist['href'] += search_result["id"]["playlistId"]
            playlist['id'] = search_result["id"]["channelId"]
            playlists.append(playlist)

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

            videos.append(_video)

        else:
            print "Unhandled", search_result

    # for i in range(30):
    #     x = search_response.get("nextPageToken")
    #     search_response = youtube.search().list(
    #         q=options.q,
    #         maxResults=options.max_results,
    #         part="id,snippet",
    #         type='video',
    #         pageToken=x,
    #         order='viewCount',
    #         videoCategoryId='10',  # This category belong to Music & Entertaiment
    #         publishedAfter=last.strftime('%Y-%m-%dT%H:%M:%SZ'),
    #         publishedBefore=now.strftime('%Y-%m-%dT%H:%M:%SZ'),
    #     ).execute()

    return videos, channels, playlists


if __name__ == "__main__":

    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results")
    args = argparser.parse_args()

    try:
        videos, channels, playlists = youtube_search(args)

        print "#" * 20, ' Videos with link ', "#" * 20, "\n"

        c = 1
        for i in videos:
            print c, '- ', i['title']
            pprint(i)
            print '-' * 100
            c += 1

        print "#" * 60, '\n\n\n'

        # print "#" * 20, ' Channels with link ', "#" * 20, "\n"

        # c = 1
        # for i in channels:
        #     print c, '- '
        #     pprint(i)
        #     print '-' * 100
        #     c += 1

        # print "#" * 60, '\n\n\n'

        # print "#" * 20, ' Playlists with link ', "#" * 20, "\n"

        # c = 1
        # for i in playlists:
        #     print c, '- '
        #     pprint(i)
        #     print '-' * 100
        #     c += 1

        # print "#" * 60, '\n\n\n'

    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
