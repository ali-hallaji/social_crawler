import datetime
import csv
from pymongo import DESCENDING

from config.settings import BASE_DIR
from core.db import cursor


def yt_mosted_viewed():
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

    projection = {
        'thumbnails': 0,
        'img': 0,
        'keywords': 0
    }

    data = cursor.refined_data.find(criteria, projection)
    data = data.sort('daily_views_today', DESCENDING).limit(50000)

    path = BASE_DIR + '/cache/' + '{0}.csv'.format(_date.date())
    print BASE_DIR

    if data:
        fields = cursor.refined_data.find_one(criteria, projection).keys()

        with open(path, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fields)
            writer.writeheader()

            for doc in data:

                for k in doc.keys():
                    if k not in fields:
                        del doc[k]

                writer.writerow(
                    {
                        k: unicode(v).encode('utf8') for k, v in doc.items()
                    }
                )
    print 'Finished'

