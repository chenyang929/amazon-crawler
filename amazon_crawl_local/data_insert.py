import json
import time
import copy
import traceback
from store import AmazonStorePro, AmazonRedis
from settings import MYSQL_CONFIG_LOCAL, REDIS_CONFIG_LOCAL
from config import Config

sql_sku = (
    "insert into {}(scgs_uuid, scgs_products_id, scgs_url_id, scgs_brand, scgs_product_url, scgs_name,"
    "scgs_firstTitle, scgs_secondTitle, scgs_original_price, scgs_price, scgs_max_price, scgs_discount,"
    "scgs_dispatch, scgs_shipping, scgs_currency, scgs_attribute, scgs_version_urls, scgs_review_count,"
    "scgs_grade_count, scgs_sales_total, scgs_total_inventory, scgs_favornum, scgs_image_url,"
    "scgs_extra_image_urls, scgs_description, scgs_category, scgs_category_url, scgs_tags, scgs_shop_name, "
    "scgs_shop_url, scgs_generation_time, scgs_platform, scgs_platform_url, scgs_crawl_time, scgs_create_time, "
    "scgs_status, scgs_questions, scgs_is_delete, scgs_reserve_field_1, scgs_reserve_field_2,"
    "scgs_reserve_field_3, scgs_reserve_field_4, scgs_reserve_field_5, scgs_reserve_field_6,"
    "scgs_reserve_field_7)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
    "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")

sql_cate = 'insert into {}(category, url, entry, rank, create_time)values(%s,%s,%s,%s,now())'

sql_grade = (
    "insert into {}(rc_listing_id, rc_product_id, rc_product_url, rc_platform, rc_site, rc_grade_overall, rc_grade_1_count, rc_grade_2_count, rc_grade_3_count,"
    "rc_grade_4_count, rc_grade_5_count, rc_reviews_count, rc_reviews_url, is_delete, rc_reserve_1, rc_reserve_2, rc_crawl_time)"
    "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())")

sql_review = (
    "insert into {}(rc_listing_id, rc_product_id, rc_product_url, rc_platform, rc_site, rc_review_id, rc_review_time, rc_customer, rc_customer_email, rc_review_title,"
    "rc_review_content, rc_review_image, rc_review_grade, rc_review_grade_detail, is_delete, rc_reserve_1, rc_reserve_2,"
    "rc_reserve_3, rc_crawl_time)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())")


def data_insert(rds):
    if rds.exists_key(Config.REDIS_DATA_LIST):
        store = AmazonStorePro(**MYSQL_CONFIG_LOCAL)   # 服务器本地切换
        while rds.exists_key(Config.REDIS_DATA_LIST):
            item = rds.rds.rpop(Config.REDIS_DATA_LIST)
            item_json = json.loads(item)
            table = item_json['table']
            print(table)
            data = item_json['data']
            try:
                if table in (Config.MYSQL_TABLE_SKU, Config.MYSQL_TABLE_SKU_TRACK):
                    store.execute_sql(sql_sku.format(table),
                                      data['scgs_uuid'],
                                      data['scgs_products_id'],
                                      data['scgs_url_id'],
                                      data['scgs_brand'],
                                      data['scgs_product_url'],
                                      data['scgs_name'],
                                      data['scgs_firstTitle'],
                                      data['scgs_secondTitle'],
                                      data['scgs_original_price'],
                                      data['scgs_price'],
                                      data['scgs_max_price'],
                                      data['scgs_discount'],
                                      data['scgs_dispatch'],
                                      data['scgs_shipping'],
                                      data['scgs_currency'],
                                      data['scgs_attribute'],
                                      data['scgs_version_urls'],
                                      data['scgs_review_count'],
                                      data['scgs_grade_count'],
                                      data['scgs_sales_total'],
                                      data['scgs_total_inventory'],
                                      data['scgs_favornum'],
                                      data['scgs_image_url'],
                                      data['scgs_extra_image_urls'],
                                      data['scgs_description'],
                                      data['scgs_category'],
                                      data['scgs_category_url'],
                                      data['scgs_tags'],
                                      data['scgs_shop_name'],
                                      data['scgs_shop_url'],
                                      data['scgs_generation_time'],
                                      data['scgs_platform'],
                                      data['scgs_platform_url'],
                                      data['scgs_crawl_time'],
                                      data['scgs_create_time'],
                                      data['scgs_status'],
                                      data['scgs_questions'],
                                      data['scgs_is_delete'],
                                      data['scgs_reserve_field_1'],
                                      data['scgs_reserve_field_2'],
                                      data['scgs_reserve_field_3'],
                                      data['scgs_reserve_field_4'],
                                      data['scgs_reserve_field_5'],
                                      data['scgs_reserve_field_6'],
                                      data['scgs_reserve_field_7'])
                elif table == Config.MYSQL_TABLE_TOP_CATE:
                    store.execute_sql(sql_cate.format(table),
                                      data['category'],
                                      data['url'],
                                      data['entry'],
                                      data['rank'])
                elif table == Config.MYSQL_TABLE_GRADE:
                    store.execute_sql(sql_grade.format(table),
                                      data['rc_listing_id'],
                                      data['rc_product_id'],
                                      data['rc_product_url'],
                                      data['rc_platform'],
                                      data['rc_site'],
                                      data['rc_grade_overall'],
                                      data['rc_grade_1_count'],
                                      data['rc_grade_2_count'],
                                      data['rc_grade_3_count'],
                                      data['rc_grade_4_count'],
                                      data['rc_grade_5_count'],
                                      data['rc_reviews_count'],
                                      data['rc_reviews_url'],
                                      data['is_delete'],
                                      data['rc_reserve_1'],
                                      data['rc_reserve_2'],
                                      )
                elif table == Config.MYSQL_TABLE_REVIEW:
                    store.execute_sql(sql_review.format(table),
                                      data['rc_listing_id'],
                                      data['rc_product_id'],
                                      data['rc_product_url'],
                                      data['rc_platform'],
                                      data['rc_site'],
                                      data['rc_review_id'],
                                      data['rc_review_time'],
                                      data['rc_customer'],
                                      data['rc_customer_email'],
                                      data['rc_review_title'],
                                      data['rc_review_content'],
                                      data['rc_review_image'],
                                      data['rc_review_grade'],
                                      data['rc_review_grade_detail'],
                                      data['is_delete'],
                                      data['rc_reserve_1'],
                                      data['rc_reserve_2'],
                                      data['rc_reserve_3'],
                                      )
                else:
                    print('wrong table name')

            except Exception as exp:
                traceback.print_exc()
                item_json['error'] = '{!r}'.format(exp)
                rds.rds.lpush(Config.REDIS_DATA_ERROR, json.dumps(item_json))

        print('finished insert')
        store.close()
    else:
        print('no item')
        time.sleep(30)


if __name__ == '__main__':
    rds = AmazonRedis(Config.REDIS_NUM, **copy.deepcopy(REDIS_CONFIG_LOCAL))
    while True:
        data_insert(rds)
