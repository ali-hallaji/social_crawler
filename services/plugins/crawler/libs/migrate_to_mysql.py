import MySQLdb
import datetime

from pymongo import DESCENDING

# from config.settings import BASE_DIR
from config.settings import SQL_DB
from config.settings import SQL_HOST
from config.settings import SQL_PASS
from config.settings import SQL_USER
from core.db import cursor


def yt_mosted_viewed():
    mydb = MySQLdb.connect(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
    sql_cursor = mydb.cursor()

    _date = datetime.datetime.now().replace(hour=4, minute=30)
    last_date = _date - datetime.timedelta(days=1)

    criteria = {
        "$or": [
            {
                "update_video_data": {
                    "$gt": _date
                },
                "daily_views_yesterday": {
                    "$gt": 0
                }
            },
            {
                "published_at": {
                    "$gt": last_date
                }
            }
        ]
    }

    sql_column = {
        'published_at': 'ReleaseDate',
        'href': 'YTURL',
        'dislikes': 'YTDisLikes',
        'likes': 'YTLikes',
        'id': 'YTVideoID',
        'daily_views_today': 'YTDailyViews',
        'title': 'YTTitle',
        'comment_count': 'YTComments',
        'channel_title': 'YTChannel',
        'description': 'YTDescription',
        'daily_views_yesterday': 'YTDailyViewsYest',
        'channel_id': 'YTChannelID',
        'all_views': 'YTAllTimeViews',
        'category_name': 'YTCategory',
        'song_title': 'Song',
        'artist': 'Artist'
    }

    projection = {}
    for i in sql_column.keys():
        projection[i] = 1

    data = cursor.refined_data.find(
        criteria,
        projection,
        no_cursor_timeout=True
    )
    data = data.sort('daily_views_today', DESCENDING).limit(50000)
    # path = BASE_DIR + '/cache/' + '{0}.csv'.format(_date.date())

    if data:

        count = 1
        for doc in data:
            new_doc = {}

            for k, v in doc.items():
                if k != '_id':
                    new_doc[sql_column[k]] = v

            new_doc['Date'] = datetime.datetime.now().replace(hour=6, minute=0)
            new_doc['Date'] = str(new_doc['Date'].date())
            new_doc['ReleaseDate'] = str(new_doc['ReleaseDate'].date())
            new_doc['Chart_type'] = 'YouTube'
            new_doc['Rank'] = count

            try:
                qmarks = ', '.join('?' * len(new_doc))
                qry = "Insert Into songs_chart (%s) Values (%s)" % (
                    qmarks,
                    qmarks
                )
                sql_cursor.execute(qry, new_doc.keys() + new_doc.values())
                mydb.commit()

            except MySQLdb.IntegrityError as e:
                print str(e)
                qry = 'UPDATE songs_chart SET {}'.format(
                    ', '.join('{}=%s'.format(k) for k in new_doc)
                )
                sql_cursor.execute(qry, new_doc.values())
                mydb.commit()

            count += 1

    print 'Finished'

