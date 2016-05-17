import gdata.youtube
import gdata.youtube.service


def search(keyword):
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.developer_key = "AIzaSyD9O5FIwU3V1teLw0UcssN8TxL7Zl15erA"

    url = 'https://gdata.youtube.com/feeds/api/videos?'
    url += 'q=football+-soccer'
    url += '&orderby=viewCount'
    url += '&start-index=11'
    url += '&max-results=10'
    # url += '&v=2'
    search = yt_service.GetYouTubeRelatedVideoFeed(url)
    print search

search('asas')
