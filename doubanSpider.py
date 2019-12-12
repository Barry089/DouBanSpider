import sys
from importlib import reload
import time
from urllib import request
from urllib.parse import quote_plus
# import requests
import numpy as np
from bs4 import BeautifulSoup
# from openpyxl import Workbook


reload(sys)


hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0'}]


def book_spider(book_tag):
    page_num = 0
    book_list = []
    try_times = 0

    while 1:
        url = 'http://www.douban.com/tag/'+quote_plus(book_tag)+'/book?start='+str(page_num*15)
        time.sleep(np.random.rand()*5)

        try:
            req = request.Request(url, headers=hds[page_num % len(hds)])
            source_code = request.urlopen(req).read()
            plain_text = str(source_code)
        except (request.HTTPError, request.URLError) as e:
            print(e)
            continue

        soup = BeautifulSoup(plain_text)
        list_soup = soup.find('div', {'class': 'mod book-list'})

        try_times += 1
        if list_soup == None and try_times < 200:
            continue
        elif list_soup == None or len(list_soup) <= 1:
            break

        for book_info in list_soup.findAll('dd'):
            title = book_info.find('a', {'class': 'title'}).string.strip()
            desc = book_info.find('div', {'class': 'desc'}).string.strip()
            desc_list = desc.split('/')
            book_url = book_info.find('a', {'class': 'title'}).get('href')

            try:
                author_info = '作者/译者：' + '/'.join(desc_list[0:-3])
            except:
                author_info = '作者/译者：暂无'

            try:
                pub_info = '出版信息：' + '/'.join(desc_list[-3:])
            except:
                pub_info = '出版信息：暂无'

            try:
                rating = book_info.find('span', {'class':'rating_nums'}).string.strip()
            except:
                rating = '0.0'

            try:
                people_num = get_people_num(book_url)
                people_num = people_num.strip('人评价')
            except:
                people_num = '0'

            book_list.append([title, rating, people_num, author_info, pub_info])
            try_times = 0

        page_num += 1
        print('Downloading information From Page %d' % page_num)

    return book_list


def get_people_num(url):
#   url = 'http://book.douban.com/subject/6082808/?from=tag_all'
    try:
        req = request.Request(url, headers = hds[np.random.randint(0, len(hds))])
        source_code = request.urlopen(req).read()
        plain_text = str(source_code)
        soup = BeautifulSoup(plain_text)
        people_num = soup.find('div', {'class': 'rating_sum'}).findAll('span')[1].string.strip()

        return people_num

    except (request.HTTPError, request.URLError) as e:
        print(e)


def do_spider(book_tag_lists):
    book_lists = []
    for book_tag in book_tag_lists:
        book_list = book_spider(book_tag)
        book_list = sorted(book_list, key=lambda x: x[1], reverse=True)
        book_lists.append(book_list)

    return book_lists


if __name__ == '__main__':
    book_tag_lists = ['个人管理', '时间管理', '投资', '文化', '宗教']
    book_lists = do_spider(book_tag_lists)
