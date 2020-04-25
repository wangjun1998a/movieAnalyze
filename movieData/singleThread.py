#!/user/bin/python
# -*-coding:utf-8-*-
import json
import os
import re
import threading
import urllib.request

import pandas as pd
import requests
from bs4 import BeautifulSoup
from snownlp import SnowNLP

# 头文件
header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'


def handlingText(text):
    """
    词性分析
    :param text: 句子
    :return: 无返回值
    """
    s = SnowNLP(text)
    # print(s.words)
    print(f'当前线程:{threading.current_thread()};', text, s.sentiments)


def iterList(rootDir, node):
    """
    遍历文件列表
    :param rootDir: 根路径
    :param node: 文件名称
    :return: 无返回值
    """
    print(node, '-' * 100)
    with open(file=f'{rootDir}/{node}', mode="r", encoding='utf-8')as file:
        results = file.readlines()
        print(results)
        map = {'力荐': 1, '推荐': 0.5, '还行': 0, '较差': -0.5, '很差': -1}
        for res in range(len(results)):
            # 将分词转换成 DataFrame
            article = pd.DataFrame({"word": [results[res][0:2]]})
            # 将词汇字典也转换成 DataFrame
            wordId = pd.DataFrame({"word": [s[0] for s in map.items()], "id": [s[1] for s in map.items()]})
            # 对字典设置索引
            wordId.set_index("word")
            # 进行匹配
            df_inner = pd.merge(article, wordId, how="inner")
            # 正确匹配数值
            if len(list(df_inner["id"])):
                print(len(list(df_inner["id"])), " --->  ", list(df_inner["id"]))
                # TODO 完成数值的存取逻辑


def iterFiles():
    """
    打开文件
    :return: 无返回值
    """
    rootDir = './files'
    list = os.listdir(rootDir)
    for d in list:
        iterList(rootDir, d)


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

    divData = soupComment.findAll('div', 'comment')
    onePageComments = []
    for div in divData:
        text = div.findAll('span', 'short')[0].getText()
        grade = ''
        if div.find_all('span', re.compile('rating')):
            grade = div.find_all('span', re.compile('rating'))[0].attrs['title']
            onePageComments.append(grade + " " + text + '\n')
    return onePageComments


def getData(count):
    """
    获取豆瓣首页的热门电影数据
    :param count: 需要爬取的数据条数
    :return: 数据集合
    """
    url = f'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit={count}' \
          f'&page_start=0'
    headers = {
        'User-Agent': header
    }
    json_data = requests.get(url, headers=headers)
    data = json_data.text
    json_data = json.loads(data)
    subjects = json_data['subjects']
    results = []
    for movie in subjects:
        row = {
            'movie_rate': movie['rate'],
            'movie_name': movie['title'],
            'movie_url': movie['url']
        }
        results.append(row)
    return results


def insertDocument(data):
    """
    插入文档
    :param data: 数据聚集合
    :return: 无返回值
    """
    for d in data:
        movie_name = d.get('movie_name')
        with open(file=f'./files/{movie_name}.txt', mode='w', encoding="utf-8") as files:
            movie_url = d.get('movie_url')
            for page in range(10):  # 豆瓣爬取多页评论需要验证。
                url = f'{movie_url}comments?start=' \
                      + str(20 * page) + \
                      '&limit=20&sort=new_score&status=P'
                print(f'当前线程:{threading.current_thread()};'
                      f'当前处理: {movie_name} ---> 第 {(page + 1)} 页的评论;'
                      f'目标URL地址:{url}')
                for i in getComment(url):
                    files.write(i)


if __name__ == '__main__':
    # insertDocument(getData(5))
    iterFiles()
