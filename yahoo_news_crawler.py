# -*- coding: utf-8 -*-

import re
import urllib.parse
from bs4 import BeautifulSoup
import requests

import numpy as np
import csv
import time


def download(url):
    if url is None:
        return None
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        return r.text

    return None


def get_new_data(soup, source='init'):
    date = 'no date'
    data = []
    if source == 'init':
        news = soup.find_all('a', href=re.compile("/news/"))

        for i in news:
            news_name = i.get_text()
            data.append(news_name)

    elif source == 'news_link':
        news_content = soup.find_all('p', class_=re.compile("canvas-atom"))

        for j in news_content:
            content = j.contents[0].string

            if content != None:
                data.append(content)

        date = soup.find('time', class_=re.compile("date")).get_text()

    return data, date


def get_new_urls(soup):
    new_urls = []
    # extract the <a> tag
    links = soup.find_all('a', href=re.compile(r"/news/.*"))

    for link in links:
        new_urls.append(link['href'])

    # print(new_urls)
    return new_urls


if __name__ == "__main__":
    with open('/.csv',
              'w', newline='') as csv_file1:

        field_names = ['index', 'datetime', 'news title', 'link', 'content']
        # it has to include the parameter of 'newline' in case blank row has been written in
        csv_writer1 = csv.DictWriter(csv_file1, fieldnames=field_names)
        csv_writer1.writeheader()

    idx = 1
    page = 4
    for i in range(1, page + 1):
        url_download = download("https://tw.stock.yahoo.com/q/h?s=4141&pg=" + str(i))
        soup = BeautifulSoup(url_download, 'html.parser', from_encoding='utf-8')
        news_list, _ = get_new_data(soup)

        content_url = get_new_urls(soup)

        assert np.array(news_list).shape[0] == np.array(content_url).shape[0]  # make sure not download duplicated link
        num_url = np.array(content_url).shape[0]

        with open('/.csv',
                  'a', newline='') as csv_file1:

            for j in range(num_url):

                try:
                    news_link = 'https://tw.stock.yahoo.com' + content_url[j]
                    news_download = download(news_link)
                    news_soup = BeautifulSoup(news_download, 'html.parser', from_encoding='utf-8')
                    contents, date = get_new_data(news_soup, source='news_link')

                    # clean data
                    cont = ''
                    for m in contents:
                        cont += m

                    csv_writer1 = csv.DictWriter(csv_file1, fieldnames=field_names)
                    info = {
                        'index': idx,
                        'datetime': date,
                        'news title': news_list[j],
                        'link': news_link,
                        'content': cont
                    }

                    csv_writer1.writerow(info)
                    idx += 1

                except Exception as e:
                    print(e)
                    pass

                time.sleep(1)
