from store import AmazonStorePro, AmazonRedis
from settings import MYSQL_CONFIG_LOCAL, MYSQL_CONFIG_SERVER, REDIS_CONFIG_LOCAL

amazon_store = AmazonStorePro(**MYSQL_CONFIG_LOCAL)

sql_1 = "select category, entry, url from amazon_top_category"

sql_2 = "select wtc_id from crawler_amazon_track_task where wtc_task_category=%s and wtc_task_type=%s " \
        "and wtc_task_site='com'"

sql_3 = "update crawler_amazon_track_task set wtc_task_info=%s where wtc_task_category=%s and wtc_task_type=%s " \
        "and wtc_task_site='com'"

sql_4 = "insert into crawler_amazon_track_task(wtc_task_category, wtc_task_type, wtc_task_info, wtc_task_site, " \
        "wtc_status, wtc_is_delete, wtc_create_time)values(%s,%s,%s,'com', 3, 0, now())"

sql_5 = "select wtc_id, wtc_task_category,wtc_task_type from crawler_amazon_track_task where wtc_task_site='com'"

sql_6 = "select id from amazon_top_category where category=%s and entry=%s"

sql_7 = "update crawler_amazon_track_task set wtc_status=5 where wtc_id=%s"

sql_truncate = "truncate amazon_top_category"


rows = amazon_store.execute_sql(sql_1)
rows_set = set()
for row in rows:
    key = '{}{}'.format(row['category'], row['entry'])
    if key in rows_set:
        continue
    rows_set.add(key)
    print(row)
    _id = amazon_store.execute_sql(sql_2, row['category'], row['entry'])
    if _id:
        amazon_store.execute_sql(sql_3, row['url'], row['category'], row['entry'])
    else:
        amazon_store.execute_sql(sql_4, row['category'], row['entry'], row['url'])

amazon_store.execute_sql(sql_truncate)

# 找出已不存在的category，不用
# rows = amazon_store.execute_sql(sql_5)
# for row in rows:
#     _id = amazon_store.execute_sql(sql_6, row['wtc_task_category'], row['wtc_task_type'])
#     if not _id:
#         print(row['wtc_id'])
#         amazon_store.execute_sql(sql_7, row['wtc_id'])
