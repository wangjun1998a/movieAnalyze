#!/user/bin/python
# -*-coding:utf-8-*-
import json
import os
import re
import threading
import urllib.request

import jieba
import pandas as pd
import requests
from bs4 import BeautifulSoup
from snownlp import SnowNLP
from pyecharts.charts import Bar, WordCloud

# 头文件
header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'


def produceCharts(xData, yData, node):
    """
    图形展示
    :return: 无返回值
    """
    bar = Bar()
    bar.add_xaxis(xData)
    bar.add_yaxis("次数", yData)
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    # 也可以传入路径参数，如 bar.render("mycharts.html")
    bar.render(f"./histogram/{node.replace('.txt', '.html')}")


def analysisWords(rootDir, node):
    """
    词云分析
    :param rootDir: 路径
    :param node: 文件名称
    :return: 无返回值
    """

    # TODO 词云的数据展示
    # 读取文件并去除用户评分数据
    with open(file=f'{rootDir}/{node}', mode="r", encoding='utf-8')as file:
        content = file.read() \
            .replace('力荐 ', '') \
            .replace('推荐 ', '') \
            .replace('还行 ', '') \
            .replace('较差 ', '') \
            .replace('很差 ', '')
        cut = jieba.cut(content)
        seaCut = jieba.cut_for_search(content)
        # 截取数据
        cut_content = ' '.join(cut)
        # 分割成数组
        cut_content = cut_content.split(' ')
        # TODO 使用字典去存储数据
        wordMap = {}
        for c in cut_content:
            if wordMap.get(c):
                # 如果值存在 拿出来然后+1
                wordMap[c] = int(wordMap.get(c)) + 1
            else:
                wordMap[c] = 1
        # 移除错误数据
        wordMap.pop('')
        # TODO 提取字典转换成元祖,放入数组中
        wordArray = []
        for key in wordMap:
            if len(key) == 1:
                continue
            else:
                wordArray.append((key, wordMap[key]))

    # 创建词云对象
    (WordCloud()
     .add(series_name="热点分析", data_pair=wordArray, word_size_range=[6, 66])
     .render(f"./wordCloud/{node.replace('.txt', '.html')}"))


def handlingText(text):
    """
    词性分析
    :param text: 句子
    :return: 无返回值
    """
    s = SnowNLP(text)
    # print(s.words)
    # print(f'当前线程:{threading.current_thread()};', text, s.sentiments)
    # print(f'当前线程:{threading.current_thread()};', text)
    return s.sentiments


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
        map = {'力荐': 1, '推荐': 0.5, '还行': 0, '较差': -0.5, '很差': -1}
        # 柱状图X轴
        xData = [key for key in map.keys()]
        # 柱状图Y轴
        yData = []
        # 力荐次数
        testimonials = 0
        # 推荐次数
        recommend = 0
        # 还行次数
        ok = 0
        # 较差次数
        poor = 0
        # 很差次数
        bad = 0
        for res in range(len(results)):
            # 情感分析数值
            emotionalScore = handlingText(results[res])
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
                if float(0.8) <= emotionalScore <= float(1) and float(list(df_inner["id"])[0]) == 1:
                    testimonials += 1
                elif float(0.6) < emotionalScore <= float(0.8) and float(list(df_inner["id"])[0]) == 0.5:
                    recommend += 1
                elif float(0.5) < emotionalScore <= float(0.6) and float(list(df_inner["id"])[0]) == 0:
                    ok += 1
                elif float(0.3) < emotionalScore <= float(0.50) and float(list(df_inner["id"])[0]) == -0.5:
                    poor += 1
                elif float(0) < emotionalScore <= float(0.30) and float(list(df_inner["id"])[0]) == -1:
                    bad += 1
        # TODO 数值存入数组中 yData
        yData.append(testimonials)
        yData.append(recommend)
        yData.append(ok)
        yData.append(poor)
        yData.append(bad)
        # TODO 柱状图生成
        produceCharts(xData, yData, node)
        # TODO 数据分析(词云)
        analysisWords(rootDir, node)


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
