import copy
from settings import REDIS_CONFIG_LOCAL, MYSQL_CONFIG_LOCAL
from store import AmazonRedis, AmazonStorePro
from config import Config


rds = AmazonRedis(2, **copy.deepcopy(REDIS_CONFIG_LOCAL))

asin_set = set()
with open('asin', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            asin_set.add(line)

print(asin_set)
# 1、选择站点
suffix = 'com'   # com\co.uk\co.jp\fr\it\es\de\in\ca
# 2、选择采集类型
entry = 7   # 1详情、7评论

task_lst = []
for asin in asin_set:
    mp = {'entry': entry}
    if entry == Config.DETAIL:
        mp['page_url'] = "https://www.amazon.{}/dp/{}".format(suffix, asin)
        task_lst.append(mp)

    elif entry == Config.COMMENT:
        # 3、1表示采全部星级，0表示采特定星级
        all_star = 1
        if all_star:
            mp['page_url'] = "https://www.amazon.{suffix}/product-reviews/{asin}/?&pageNumber=1" \
                             "&pageSize=50&sortBy=recent".format(suffix=suffix, asin=asin)
            mp['asin'] = asin
            mp['listing_id'] = ''
            # 5、是否有采集日期限制
            mp['date'] = ''
            task_lst.append(mp)
        else:
            # 4、选取星级
            stars = [1, 2, 3, 4]
            for star in stars:
                new_mp = {'entry': entry}
                if star == 1:
                    star = 'one'
                elif star == 2:
                    star = 'two'
                elif star == 3:
                    star = 'three'
                elif star == 4:
                    star = 'four'
                else:
                    star = 'five'
                new_mp['page_url'] = "https://www.amazon.{suffix}/product-reviews/{asin}/?pageNumber=1&pageSize=50" \
                                     "&sortBy=recent&filterByStar={star}_star".format(suffix=suffix, asin=asin, star=star)
                new_mp['asin'] = asin
                new_mp['listing_id'] = ''
                # 5、是否有采集日期限制
                new_mp['date'] = ''
                task_lst.append(new_mp)


for task in task_lst:
    print(task)
    rds.rds.rpush(Config.REDIS_START_URLS, task)
