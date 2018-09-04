import pymysql
import traceback
import sys
import csv

MYSQL_CONFIG_LOCAL = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': '123456',
    'db': 'scb_crawler_system',
    'charset': 'utf8mb4',
    }

MYSQL_CONFIG_SERVER = {
    'host': 'localhost',  # 服务器上改为localhost,47.91.140.136
    'port': 3306,
    'user': 'bgpc',
    'passwd': 'bgpc1qaz@WSX',
    'db': 'scb_crawler_system',
    'charset': 'utf8',
    'unix_socket': '/data/crawler_system/mysql_data/mysql/mysql.sock',
    }

# sql = "select scgs_uuid, scgs_products_id, scgs_url_id, scgs_brand, scgs_product_url, scgs_name," \
#       "scgs_firstTitle, scgs_secondTitle, scgs_original_price, scgs_price, scgs_max_price, scgs_discount," \
#       "scgs_dispatch, scgs_shipping, scgs_currency, scgs_attribute, scgs_version_urls, scgs_review_count," \
#       "scgs_grade_count, scgs_sales_total, scgs_total_inventory, scgs_favornum, scgs_image_url," \
#       "scgs_extra_image_urls, scgs_description, scgs_category, scgs_category_url, scgs_tags, scgs_shop_name," \
#       "scgs_shop_url, scgs_generation_time, scgs_platform, scgs_platform_url, scgs_crawl_time, scgs_create_time," \
#       "scgs_status, scgs_questions, scgs_is_delete, scgs_reserve_field_1, scgs_reserve_field_2," \
#       "scgs_reserve_field_3, scgs_reserve_field_4, scgs_reserve_field_5, scgs_reserve_field_6," \
#       "scgs_reserve_field_7 from crawler_amazon_sku where scgs_category=%s and scgs_tags=%s" \
#       "and scgs_platform_url=%s and scgs_crawl_time=%s order by scgs_favornum"


amazon_sql = "select scgs_products_id, scgs_brand, scgs_product_url, scgs_name," \
      "scgs_firstTitle, scgs_original_price, scgs_price, scgs_max_price, scgs_discount," \
      "scgs_currency, scgs_attribute, scgs_review_count," \
      "scgs_grade_count, scgs_favornum, scgs_image_url," \
      "scgs_extra_image_urls, scgs_description, scgs_category, scgs_category_url, scgs_tags, scgs_shop_name," \
      "scgs_shop_url, scgs_generation_time, scgs_platform, scgs_create_time," \
      "scgs_questions, scgs_reserve_field_1, scgs_reserve_field_2," \
      "scgs_reserve_field_3, scgs_reserve_field_4, scgs_reserve_field_6," \
      "scgs_reserve_field_7 from crawler_amazon_sku_track"

amazon_Title = ['ASIN', '品牌', '产品链接', '产品名称', '产品类目', '原价', '售价', '最高价', '折扣',
                '货币', '属性', '回复数', '评分数', '列表排名', '图片链接', '相关图片', '描述',
                '列表类目', '类目链接', '列表类型', '店铺名称', '店铺链接', '上架时间', '数据平台', '采集时间',
                '问题回答数', '评论等级百分比数', 'BSR数据', '产品技术参数', '配送方式', '跟卖卖家数',
                '跟售最低价']


class Store:
    def __init__(self, **kwargs):
        try:
            self.conn = pymysql.connect(**kwargs)
        except:
            traceback.print_exc()
            sys.exit()

    def execute_sql(self, _sql, *args):
        if 'select' in _sql:
            cur = self.conn.cursor()
            cur.execute(_sql, args)
            return cur.fetchall()
        else:
            if 'insert' in _sql or 'where' in _sql:
                cur = self.conn.cursor()
                cur.execute(_sql, args)
                self.conn.commit()
            else:
                print('no where')

    def close(self):
        cursor = self.conn.cursor()
        cursor.close()
        self.conn.close()


def select_rows(sql):
    store = Store(**MYSQL_CONFIG_LOCAL)
    rows = store.execute_sql(sql)
    rows = [list(item) for item in list(rows)]
    # for row in rows:
    #     if row[0] == 4:
    #         row[0] = 'BestSellers'
    #     else:
    #         row[0] = 'NewReleases'
    #     #row.insert(0, 0)
    #     print(row)
    store.close()
    return rows


def output_csv(csv_name, sql, col_name, ):
    with open(csv_name, 'w', encoding='utf-8', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(col_name)
        rows = select_rows(sql)
        for row in rows:
            spamwriter.writerow(row)


if __name__ == '__main__':
    csv_title = '澳洲一级类目采集结果.csv'
    #slt_sql = "select entry, category, url, rank from amazon_top_category_new"
    #print(select_rows(slt_sql))
    #col_title = ['榜单类型', '类目结构', '类目链接', '类目层级']
    # output_csv(csv_title, slt_sql, col_title)
    output_csv(csv_title, amazon_sql, amazon_Title)
