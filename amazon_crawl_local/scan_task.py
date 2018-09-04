import datetime
import json
import time
import random
import requests
from lxml import etree
from settings import MYSQL_CONFIG_SERVER, MYSQL_CONFIG_LOCAL, HEADERS
from store import AmazonStorePro


def scan_database(rds, conf):
    # headers = {'User-Agent': random.choice(HEADERS)}
    # jollychic_url = 'https://www.jollychic.com/delivery.html'
    # resp = requests.get(jollychic_url, headers=headers)
    # sel = etree.HTML(resp.text)
    # country_lst = sel.xpath('//dl[@class="delivery-chose-select fn-hide J-delivery-cnt J-delivery-country"]/dd')
    # for country in country_lst:
    #     country_id = country.xpath('./@data-value')[0].strip()
    #     country_name = country.xpath('./text()')[0].strip()
    #     data = {
    #         'regionId': country_id,
    #         'configType': '1',
    #         'type': 'country',
    #         'countryId': country_id,
    #         'provinceId': '0',
    #         'cityId': '0'
    #     }
    #     dt = {'site': 'jollychic', 'url': 'https://www.jollychic.com/DeliveryAction/ajaxGetRegionShippingFee',
    #           'country': country_name, 'data': data}
    #     mp = json.dumps(dt)
    #     print(mp)
    #     print(country_id, country_name)
    #     rds.rds.rpush(conf.REDIS_START_URLS, mp)
    sign = False
    try:
        store = AmazonStorePro(**MYSQL_CONFIG_LOCAL)   # 服务器本地切换

        sql_update_status = "update crawler_amazon_track_task set wtc_status=%s, wtc_crawl_time=now() where wtc_id=%s"

        sql_select_track = (
            "select wtc_id, wtc_task_type, wtc_task_frequency, wtc_task_period, wtc_task_info,wtc_task_category, "
            "wtc_crawl_time, wtc_create_time, wtc_task_site from crawler_amazon_track_task_copy "
            "where wtc_status=%s and wtc_is_delete=%s")

        rows = store.execute_sql(sql_select_track, 1, 0)
        for row in rows:
            task_id = row['wtc_id']
            task_type = row['wtc_task_type']
            task_frequency = row['wtc_task_frequency']
            task_period = row['wtc_task_period']
            task_info = row['wtc_task_info']
            task_category = row['wtc_task_category']
            start_track_time = row['wtc_create_time']
            last_track_time = row['wtc_crawl_time']

            # 非首次采集
            if last_track_time is not None:
                end_track_time = start_track_time + datetime.timedelta(days=task_period)
                next_track_time = last_track_time + datetime.timedelta(days=task_frequency)
                now_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                if next_track_time > end_track_time:
                    store.execute_sql(sql_update_status, 2, task_id)
                if now_time > next_track_time:
                    sign = True
                    page_url = task_info.strip()
                    mp = {'entry': task_type, 'page_url': page_url, 'task_category': task_category}
                    #store.execute_sql(sql_update_status, 1, task_id)
                    rds.rds.rpush(conf.REDIS_START_URLS, mp)
                    print('track: %s' % task_id)
            else:
                sign = True
                page_url = task_info.strip()
                mp = {'entry': task_type, 'page_url': page_url, 'task_category': task_category}
                #store.execute_sql(sql_update_status, 1, task_id)
                rds.rds.rpush(conf.REDIS_START_URLS, mp)
                print('track: %s' % task_id)

        store.close()
    except Exception as err:
        print('scan_database raise a error: {!r}'.format(err))
    return sign


if __name__ == '__main__':
    pass
