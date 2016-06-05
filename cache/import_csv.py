import csv
import MySQLdb
from yu import build_sql

 
mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='1234',
    db='yt')

cursor = mydb.cursor() 
csv_data = csv.reader(file('2016-06-05.csv'))

count = 1

for row in csv_data:
	if count == 1:
	    fields = row
	    print len(fields)
	    count += 1
	    continue
	    sql = build_sql('2016-06-05.csv', tablename='foo', decimalplace= 2, padding=3)
	    print sql
	    cursor.execute(sql)
	    mydb.commit()
	    continue
	
	query = "INSERT INTO foo(daily_views_yesterday, channel_title, description, title, all_views, dislikes, published_at, category_id, has_yesterday, channel_id, comment_count, href, likes, created_date, daily_views_today, _id, id, favorite_count, update_video_data)  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);".format(tuple(fields))
	print 11111111111, query
	cursor.execute(query, row)
	count += 1
 
# close the connection to the database.
mydb.commit()
cursor.close()
print "Done" 
# sql = build_sql('2016-06-05.csv', tablename = 'yourtable', decimalplace= 2, padding =3)
