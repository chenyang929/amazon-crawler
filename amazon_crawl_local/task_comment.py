import datetime
from settings import MYSQL_CONFIG_SERVER, MYSQL_CONFIG_LOCAL
from store import AmazonStorePro
import time


def scan_database(rds, conf):
    sign = False
    try:
        store = AmazonStorePro(**MYSQL_CONFIG_LOCAL)   # 服务器本地切换

        sql_select = (
            "select listing_id, product_id, site from bi_rc_task_center "
            "where create_time=%s and platform=%s")
        today = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
        yesterday = today - datetime.timedelta(days=4)
        rows = store.execute_sql(sql_select, yesterday, 'amazon')
        sites = {'US': 'com', 'UK': 'co.uk', 'FR': 'fr', 'DE': 'de', 'ES': 'es', 'CA': 'ca', 'IT': 'it',
                 'IN': 'in', 'JP': 'co.jp', 'AU': 'com.au', 'MX': 'com.mx'}
        for row in rows:
            listing_id = row['listing_id']
            product_id = row['product_id']
            site = row['site']
            unique_comment = '{}{}'.format(product_id, site)
            if rds.is_member(conf.REDIS_REVIEW_ASIN, unique_comment):
                continue
            rds.add_set(conf.REDIS_REVIEW_ASIN, unique_comment)
            date_limit = ''
            latest_comment_date = rds.get_hash_field(conf.REDIS_REVIEW_DATE, unique_comment)
            if latest_comment_date:
                if isinstance(latest_comment_date, bytes):
                    latest_comment_date = latest_comment_date.decode('utf-8')
                print(latest_comment_date)
                date_limit = latest_comment_date
            suffix = sites[site]
            page_url = "https://www.amazon.{suffix}/product-reviews/{asin}/?&pageNumber=1" \
                       "&pageSize=50&sortBy=recent".format(suffix=suffix, asin=product_id)
            mp = {'entry': conf.COMMENT, 'page_url': page_url, 'asin': product_id,
                  'listing_id': listing_id, 'date': date_limit}
            rds.rds.rpush(conf.REDIS_START_URLS, mp)
        rds.delete_key(conf.REDIS_REVIEW_ASIN)
        store.close()
    except Exception as err:
        print('scan_database raise a error: {!r}'.format(err))
    return sign


if __name__ == '__main__':
    pass
