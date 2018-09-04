# -*- coding: utf-8 -*-
from store import AmazonStorePro
from settings import MYSQL_CONFIG_SERVER
import re

store_server = AmazonStorePro(**MYSQL_CONFIG_SERVER)

sql_insert = ("insert into crawler_amazon_track_task(wtc_task_type, wtc_task_frequency, wtc_task_period,"
              "wtc_task_info, wtc_task_category,wtc_task_site,wtc_status, wtc_is_delete, wtc_create_time)"
              "values(%s,%s,%s,%s,%s,%s,%s,%s,now())")


sql_select = ("select wtc_id from crawler_amazon_track_task where wtc_task_category=%s and wtc_task_type=%s "
              "and wtc_task_site=%s")


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

task_set = set()
count = 0
if len(category_lst) == len(url_lst):
    entry = 5   # 确定类别，热销和新品分开导入
    status = 3
    is_delete = 0
    for i in range(len(category_lst)):
            category = category_lst[i]
            url = url_lst[i]
            suffix = re.findall(r'www.amazon.(.*?)/', url)[0]
            key = '{}@{}@{}'.format(category, entry, suffix)
            if key in task_set:
                print('exist')
                continue
            task_set.add(key)
            frequency = 1
            period = 365
            _id = store_server.execute_sql(sql_select, category, entry, suffix)
            if not _id:
                print(category, entry, suffix)
                count += 1
                store_server.execute_sql(sql_insert, entry, frequency, period, url, category, suffix, status, is_delete)
print(count)
print(len(task_set))
