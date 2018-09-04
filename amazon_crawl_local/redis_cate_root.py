import copy
from settings import HEADERS, REDIS_CONFIG_LOCAL, MYSQL_CONFIG_LOCAL
from store import AmazonRedis, AmazonStorePro
from config import Config
import random
import requests
from lxml import etree
from parse_html import push_data_into_redis


def get_root_category(rds, root_url, cate_entry):
    headers = {'user-agent': random.choice(HEADERS)}
    req = requests.get(root_url, headers=headers)
    if req.status_code == 200:
        sel = etree.HTML(req.text)
        root_category = sel.xpath('//ul[@id="zg_browseRoot"]/ul/li/a')
        for rc in root_category:
            url = rc.xpath('./@href')[0]
            cate = rc.xpath('./text()')[0]
            print(cate, url)
            if cate_entry == Config.SHAKE:
                cate_mp = {
                    'category': cate,
                    'url': url,
                    'entry': cate_entry,
                    'rank': 1
                }
                data_mp = {"table": Config.MYSQL_TABLE_TOP_CATE, "data": cate_mp}
                push_data_into_redis(rds, Config, data_mp)

            else:
                if cate in cate_set:
                    mp = {'entry': Config.CATE, 'page_url': url, 'cate_entry': cate_entry}
                    rds.rds.rpush(Config.REDIS_START_URLS, mp)

    else:
        print(req.status_code)


if __name__ == '__main__':
    cate_set = set()
    with open('cate_root', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                cate_set.add(line.strip())
    print(cate_set)
    rds = AmazonRedis(2, **copy.deepcopy(REDIS_CONFIG_LOCAL))
    root_url = 'https://www.amazon.com/gp/new-releases/'
    cate_entry = 5
    get_root_category(rds, root_url, cate_entry)


