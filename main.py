#!/usr/bin/python
# coding: utf-8
import sys
import bs4
import requests


def crawl_search(search_keyword):
    list_of_url = []

    if ' ' in search_keyword:
        search_keyword = search_keyword.replace(' ', '+')

    url = 'https://www.youtube.com/results?search_sort=video_view_count'
    url += '&filters=today'
    url += '&search_query=' + search_keyword
    url += '&page=1'
    # url += '&max_results=2'

    text = requests.get(url).text
    soup = bs4.BeautifulSoup(text, "lxml")

    div = [d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class']]

    for d in div:
        img0 = d.find_all('img')[0]
        a0 = d.find_all('a')[0]

        main_img = img0['src'] if not img0.has_attr('data-tumb') else img0['data-tumb']
        a0 = [x for x in d.find_all('a') if x.has_attr('title')][0]
        title = a0['title']
        link = 'https://www.youtube.com' + a0['href'],

        list_of_url.append(
            [
                main_img,
                link,
                title
            ]
        )

    return list_of_url


if __name__ == '__main__':
    search_keyword = '+'.join(sys.argv[1:])

    for i in crawl_search(search_keyword):
        print i

