
class Config:
    # mysql表名
    MYSQL_TABLE_SKU = 'crawler_amazon_sku'
    MYSQL_TABLE_SKU_TRACK = 'crawler_amazon_sku_track'
    MYSQL_TABLE_TOP_CATE = 'amazon_top_category'
    MYSQL_TABLE_GRADE = 'crawler_rc_grade'
    MYSQL_TABLE_REVIEW = 'crawler_rc_review'

    # 任务标签分类
    DETAIL = 1
    LIST = 2
    KEY = 3
    BEST = 4
    NEW = 5
    SHAKE = 6
    COMMENT = 7
    CATE = 8

    # 并发数
    CONCURRENT = 80

    # 代理
    REMAIN = 160
    FAIL_TIMES = 1

    # 超时
    TIMEOUT = 30

    # redis目录设置
    REDIS_NUM = 2
    REDIS_DIR = ''
    REDIS_DATA_LIST = 'datalist'
    REDIS_DATA_ERROR = 'dataerror'
    REDIS_START_URLS = 'start'
    REDIS_REQUEST_URLS = 'request'
    REDIS_CRAWL_URLS = 'crawl'
    REDIS_ERROR_URLS = 'error'
    REDIS_REVIEW_ASIN = 'unique_comment'
    REDIS_REVIEW_DATE = 'comment_date'


if __name__ == '__main__':
    pass
