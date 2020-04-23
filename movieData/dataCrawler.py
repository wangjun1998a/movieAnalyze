import json
import urllib.request

import requests
from bs4 import BeautifulSoup

# 头文件
header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'


def getHtml(url):
    """
    获取url页面
    :param url: url
    :return: html files
    """
    headers = {'User-Agent': header}
    req = urllib.request.Request(url, headers=headers)
    req = urllib.request.urlopen(req)
    content = req.read().decode('utf-8')

    return content


def getComment(url):
    """
    解析HTML页面
    :param url:  url
    :return: 页面
    """
    html = getHtml(url)
    soupComment = BeautifulSoup(html, 'html.parser')

    comments = soupComment.findAll('span', 'short')
    onePageComments = []
    for comment in comments:
        # print(comment.getText()+'\n')
        onePageComments.append(comment.getText() + '\n')

    return onePageComments


def get_data():
    """
    获取豆瓣首页的热门电影数据
    :return:
    """
    url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=300&page_start=0'
    # url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=330&page_start=0'
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        'User-Agent': header
    }
    json_data = requests.get(url, headers=headers)
    # print(json_data.text)
    data = json_data.text
    json_data = json.loads(data)
    subjects = json_data['subjects']
    result = []
    for movie in subjects:
        row = {
            'movie_rate': movie['rate'],
            'movie_name': movie['title'],
            'movie_url': movie['url']
        }
        result.append(row)
    return result


if __name__ == '__main__':
    # f = open('我不是药神page10.txt', 'w', encoding='utf-8')
    result = get_data()
    for res in result:
        movie_url = res.get('movie_url')
        for page in range(10):  # 豆瓣爬取多页评论需要验证。
            url = f'{movie_url}comments?start=' + str(
                20 * page) + '&limit=20&sort=new_score&status=P'
            print('第%s页的评论:' % (page + 1))
            print(url + '\n')

            for i in getComment(url):
                # f.write(i)
                print(i)
            print('-' * 60)
