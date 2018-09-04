# -*- coding: utf-8 -*-
from store import AmazonStorePro, AmazonRedis
import copy
from settings import REDIS_CONFIG_LOCAL, MYSQL_CONFIG_LOCAL, MYSQL_CONFIG_SERVER
from config import Config

rds = AmazonRedis(2, **copy.deepcopy(REDIS_CONFIG_LOCAL))

category_lst = []
with open('category', encoding='utf-8') as f:
    for line in f:
        if len(line) > 0:
            line = '>'.join([item.strip() for item in line.strip().split('>')])
            category_lst.append(line)

url_lst = []
with open('url', encoding='utf-8') as f:
    for line in f:
        if len(line) > 0:
            line = line.strip()
            url_lst.append(line)
print(len(category_lst))
print(len(url_lst))

if len(category_lst) == len(url_lst):
    entry = 6   # 确定类别，热销和新品分开导入
    for i in range(len(category_lst)):
            category = category_lst[i]
            url = url_lst[i]
            mp = {'entry': entry, 'page_url': url, 'task_category': category}
            rds.rds.rpush(Config.REDIS_START_URLS, mp)
