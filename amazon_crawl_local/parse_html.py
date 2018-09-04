from datetime import datetime
import re
import json
import time
import uuid
from lxml import etree
from parse_product_html import SiteType, ParseProduct
from parse_comment_html import Comment


def exist_captcha(html):
    sel = etree.HTML(html)
    captcha = sel.xpath('//input[@id="captchacharacters"]')
    if captcha:
        return True
    return False


def choose_parse(rds, conf, mp, html):
    mapping = eval(mp)
    entry = int(mapping['entry'])
    sel = etree.HTML(html)
    if entry in (conf.LIST, conf.KEY):
        items = sel.xpath('//ul[starts-with(@class, "s-result")]/li[@data-asin]')
        if items:
            parse_list(rds, conf, mp, html)
        else:
            rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
    elif entry in (conf.BEST, conf.NEW, conf.SHAKE):
        items_1 = sel.xpath('//div[starts-with(@class, "zg_itemImmersion")]')
        items_2 = sel.xpath('//div[starts-with(@class, "zg_itemRow")]')  # 日站
        items_3 = sel.xpath('//ol[starts-with(@id, "zg-ordered-list")]/li')
        new = mapping.get('new', None)
        if not new:
            if items_1 or items_2:
                parse_top(rds, conf, mp, html)
            elif items_3:
                parse_top_new(rds, conf, mp, html)
            else:
                collect_error(rds, conf, mp, error='No items')
                #rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
        else:
            if new == 'y' and items_3:
                parse_top_new(rds, conf, mp, html)
            elif new == 'n' and (items_1 or items_2):
                parse_top(rds, conf, mp, html)
            else:
                collect_error(rds, conf, mp, error='No items')

    elif entry == conf.DETAIL:
        parse_product(rds, conf, mp, html)
    elif entry == conf.CATE:
        parse_cate(rds, conf, mp, html)
    elif entry == conf.COMMENT:
        parse_comment(rds, conf, mp, html)


def parse_list(rds, conf, mp, html):
    pass


def parse_top(rds, conf, mp, html):
    mapping = eval(mp)
    page_url = mapping['page_url']
    entry = mapping['entry']
    category_url = mapping.get('category_url', None)
    task_category = mapping.get('task_category', None)
    if not category_url:
        category_url = page_url
        mapping['category_url'] = page_url

    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]
    domain = SiteType[suffix]
    sign = domain['sign']
    currency = domain['currency']
    sel = etree.HTML(html)

    category = sel.xpath('//h1[@id="zg_listTitle"]/span/text()')
    if category:
        category = category[0].strip()
    else:
        category = ''
    if task_category:
        category = task_category

    products_lst_1 = sel.xpath('//div[starts-with(@class, "zg_itemImmersion")]')  # 美英法站
    products_lst_2 = sel.xpath('//div[starts-with(@class, "zg_itemRow")]')  # 日站
    products_lst = products_lst_1 if products_lst_1 else products_lst_2
    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for pl in products_lst:
        # asin
        asin = pl.xpath('.//div[@data-p13n-asin-metadata]/@data-p13n-asin-metadata')
        if asin:
            asin = eval(asin[0])['asin']
            product_url = 'https://www.amazon.{}/dp/{}'.format(suffix, asin)
            rank = pl.xpath('.//span[@class="zg_rankNumber"]/text()')
            if rank:
                rank = rank[0].strip().replace('.', '')
            else:
                rank = 0

            # if int(entry) in (conf.BEST, conf.NEW):
            #     # 类目加asin
            #     cate_asin = '{}@{}@{}@{}'.format(category, entry, suffix, asin)
            #     rds.add_set(conf.REDIS_CATE_ASIN, cate_asin)
            #
            #     # 唯一asin
            #     unique_asin = '{}@{}'.format(asin, suffix)
            #     if rds.is_member(conf.REDIS_UNIQUE_ASIN, unique_asin):
            #         repeat_mp = {'page_url': product_url, 'entry': 1, 'rank': rank, 'category_info': category,
            #                      'category_url': category_url, 'category_entry': entry, 'create_time': create_time}
            #         rds.rds.lpush(conf.REDIS_REPEAT_ASIN, repeat_mp)
            #         print('repeat asin')
            #         continue
            #     rds.add_set(conf.REDIS_UNIQUE_ASIN, unique_asin)
            try:
                price_1 = pl.xpath('.//span[starts-with(@class, "a-size-base a-color-price")]/span/text()')
                if price_1:
                    _price = ''.join(price_1).replace(sign, '').replace(currency, '').replace(' ', '').replace(
                        '\xa0', '')
                    if currency == 'EUR':
                        _price = _price.replace('.', '').replace(',', '.')
                    else:
                        _price = _price.replace(',', '')
                    if '-' in _price:
                        price, max_price = [p.strip() for p in _price.split('-')]
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = ''.join(re.findall(r'\d+\.?\d*', max_price))
                    else:
                        price = _price
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = 0
                else:
                    price = 0
                    max_price = 0

                price = float(price)
                max_price = float(max_price)
            except:
                price = 0
                max_price = 0
            percent = ''
            movement = ''
            movement_1 = 0
            movement_2 = 0
            percent_xp_1 = pl.xpath('.//span[@class="zg-percent-change"]/text()')
            percent_xp_2 = pl.xpath('.//span[@class="zg_percentChange"]/text()')
            if percent_xp_1:
                percent = percent_xp_1
            elif percent_xp_2:
                percent = percent_xp_2
            if percent:
                percent = percent[0].strip().replace(',', '')
            movement_xp_1 = pl.xpath('.//span[@class="zg-sales-movement"]/text()')
            movement_xp_2 = pl.xpath('.//span[@class="zg_salesMovement"]/text()')
            if movement_xp_1:
                movement = movement_xp_1
            elif movement_xp_2:
                movement = movement_xp_2
            if movement:
                movement = re.findall(r'\d,?\d*', movement[0])
                if len(movement) == 2:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = movement[1].replace(',', '')
                elif len(movement) == 1:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = 0
            new_mp = {'page_url': product_url, 'entry': 1, 'rank': rank, 'price': price,
                      'max_price': max_price, 'category_info': category, 'category_url': category_url,
                      'category_entry': entry, 'create_time': create_time, 'percent': percent,
                      'movement_1': movement_1, 'movement_2': movement_2}
            rds.rds.rpush(conf.REDIS_START_URLS, new_mp)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)

    # 判断是否有下一页
    current_page = sel.xpath('//ol[starts-with(@class, "zg_pagination")]/li[contains(@class, "zg_page zg_selected")]/a/@page')
    if current_page:
        current_page_num = current_page[0].strip()
        if current_page_num.isdigit():
            next_page_id = int(current_page_num) + 1
            next_page = sel.xpath('//ol[starts-with(@class, "zg_pagination")]/li/a[@page="%s"]/@href' % next_page_id)
            if next_page:
                next_page_url = next_page[0].strip()
                mapping['page_url'] = next_page_url
                mapping['new'] = 'n'
                rds.rds.lpush(conf.REDIS_START_URLS, mapping)


def parse_top_new(rds, conf, mp, html):
    mapping = eval(mp)
    page_url = mapping['page_url']
    entry = mapping['entry']
    category_url = mapping.get('category_url', None)
    task_category = mapping.get('task_category', None)
    if not category_url:
        category_url = page_url
        mapping['category_url'] = page_url

    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]
    domain = SiteType[suffix]
    sign = domain['sign']
    currency = domain['currency']

    sel = etree.HTML(html)
    category = sel.xpath('//h1/span[@class="category"]/text()')   # 不同
    if category:
        category = category[0].strip()
    else:
        category = ''
    if task_category:
        category = task_category

    products_lst_3 = sel.xpath('//ol[starts-with(@id, "zg-ordered-list")]/li')   # 不同
    if products_lst_3:
        products_lst = products_lst_3
    else:
        products_lst = ''

    create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for pl in products_lst:
        product_url = pl.xpath('.//a[contains(@class,"a-link-normal")]/@href')   # 不同
        if product_url:
            asin = re.findall(r'/dp/(.+)/ref', product_url[0])
            if asin:
                asin = asin[0].strip()
                product_url = 'https://www.amazon.{}/dp/{}'.format(suffix, asin)
            else:
                continue
            rank = pl.xpath('.//span[contains(text(), "#")]/text()')
            if rank:
                rank = rank[0].strip().replace('#', '')
            else:
                rank = 0

            # release_date = pl.xpath('.//span[@class="zg-release-date"]/text()')
            # if release_date:
            #     release_date = release_date[0]
            # print('release_date: ', release_date)

            try:
                price_1 = pl.xpath('.//span[starts-with(@class, "a-size-base a-color-price")]/span/text()')
                if len(price_1) > 0:
                    _price = ''.join(price_1).replace(sign, '').replace(currency, '').replace(' ', '').replace('\xa0', '')
                    if currency == 'EUR':
                        _price = _price.replace('.', '').replace(',', '.')
                    else:
                        _price = _price.replace(',', '')
                    if '-' in _price:
                        price, max_price = [p.strip() for p in _price.split('-')]
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = ''.join(re.findall(r'\d+\.?\d*', max_price))
                    else:
                        price = _price
                        price = ''.join(re.findall(r'\d+\.?\d*', price))
                        max_price = 0
                else:
                    price = 0
                    max_price = 0

                price = float(price)
                max_price = float(max_price)
            except:
                price = 0
                max_price = 0
            percent = ''
            movement = ''
            movement_1 = 0
            movement_2 = 0
            percent_xp_1 = pl.xpath('.//span[@class="zg-percent-change"]/text()')
            percent_xp_2 = pl.xpath('.//span[@class="zg_percentChange"]/text()')
            if percent_xp_1:
                percent = percent_xp_1
            elif percent_xp_2:
                percent = percent_xp_2
            if percent:
                percent = percent[0].strip().replace(',', '')
            movement_xp_1 = pl.xpath('.//span[@class="zg-sales-movement"]/text()')
            movement_xp_2 = pl.xpath('.//span[@class="zg_salesMovement"]/text()')
            if movement_xp_1:
                movement = movement_xp_1
            elif movement_xp_2:
                movement = movement_xp_2
            if movement:
                movement = re.findall(r'\d,?\d*', movement[0])
                if len(movement) == 2:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = movement[1].replace(',', '')
                elif len(movement) == 1:
                    movement_1 = movement[0].replace(',', '')
                    movement_2 = 0
            new_mp = {'page_url': product_url, 'entry': 1, 'rank': rank, 'price': price,
                      'max_price': max_price, 'category_info': category, 'category_url': category_url,
                      'category_entry': entry, 'create_time': create_time, 'percent': percent,
                      'movement_1': movement_1, 'movement_2': movement_2}
            rds.rds.rpush(conf.REDIS_START_URLS, new_mp)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)

    next_page = sel.xpath('//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')   # 不同
    if next_page:
        next_page_url = next_page[0].strip()
        mapping['page_url'] = next_page_url
        mapping['new'] = 'y'
        rds.rds.lpush(conf.REDIS_START_URLS, mapping)


def parse_product(rds, conf, mp, html):
    mapping = eval(mp)  # eval()函数还原存入字典值的类型
    page_url = mapping['page_url']
    entry = mapping['entry']
    category_info = mapping.get('category_info', '')
    category_url = mapping.get('category_url', '')
    category_entry = mapping.get('category_entry', entry)
    search_box = mapping.get('search_box', '')
    p_create_time = mapping.get('create_time', None)

    # 确定站点
    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]

    # 以下为传入字段
    product_url = page_url
    products_id = re.findall(r'dp/(.+)', page_url)[0]
    _uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, products_id + suffix)).replace('-', '')
    favornum = mapping.get('rank', 0)
    if int(category_entry) == conf.LIST:
        tags = 'List'
    elif int(category_entry) == conf.KEY:
        tags = 'KeyWord'
    elif int(category_entry) == conf.BEST:
        tags = 'BestSellers'
    elif int(category_entry) == conf.NEW:
        tags = 'NewReleases'
    elif int(category_entry) == conf.SHAKE:
        tags = 'MoversShakers'
    else:
        tags = 'Detail'

    sales_total = mapping.get('movement_1', '0')
    total_inventory = mapping.get('movement_2', '0')

    # 以下为页面解析字段
    product = ParseProduct(html, suffix)

    _name = product.get_title()
    if not _name:  # 舍弃没有标题的产品
        #rds.remove_member(conf.REDIS_CRAWL_URLS, mp)
        collect_error(rds, conf, mp, error='No product name')
        return

    currency = product.get_currency()

    first_title = product.get_first_title()

    second_title = ''
    if category_entry == conf.DETAIL:
        category = first_title
    elif category_entry == conf.KEY:
        second_title = category_info
        if search_box:
            category = search_box
        else:
            category = first_title
    else:
        category = category_info
        if category_entry == conf.SHAKE:
            second_title = mapping.get('percent', '')

    url_id = product.get_asin()

    brand = product.get_brand()

    discount = product.get_discount()

    original_price = product.get_original_price()
    if int(original_price) == 0:
        original_price = mapping.get('original_price', 0)

    price, max_price = product.get_price_maxprice()
    if int(price) == 0:
        price = mapping.get('price', 0)
    if int(max_price) == 0:
        max_price = mapping.get('max_price', 0)

    grade_count = product.get_grade_count()

    review_count = product.get_review_count()

    questions = product.get_questions()

    attribute = product.get_attribute()

    main_image_url = product.get_main_image()

    extra_image_urls = product.get_extra_images()

    if not main_image_url and extra_image_urls:
        main_image_url = extra_image_urls.split(',')[0]

    description = product.get_description()

    generation_time = product.get_generations_time()

    shop_name, shop_url = product.get_shop()

    reserve_field_1 = product.get_reserve_1()

    reserve_field_2 = product.get_reserve_2()

    reserve_field_3 = product.get_reserve_3()

    reserve_field_4 = product.get_reserve_4()

    reserve_field_5 = product.get_reserve_5()

    reserve_field_6, reserve_field_7 = product.get_reserve_6_7()

    if p_create_time:
        create_time = p_create_time
        crawl_time = p_create_time.split()[0]
    else:
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        crawl_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    # 以下为无需处理字段
    platform = 'amazon'
    platform_url = suffix
    dispatch = ''
    shipping = ''
    version_urls = ''
    status = 0
    is_delete = 0

    if category_entry in (conf.BEST, conf.NEW, conf.SHAKE):
        table_name = conf.MYSQL_TABLE_SKU_TRACK
    else:
        table_name = conf.MYSQL_TABLE_SKU
    sku_mp = {
            'scgs_uuid': _uuid,
            'scgs_products_id': products_id,
            'scgs_url_id': url_id,
            'scgs_brand': brand,
            'scgs_product_url': product_url,
            'scgs_name': _name,
            'scgs_firstTitle': first_title,
            'scgs_secondTitle': second_title,
            'scgs_original_price': original_price,
            'scgs_price': price,
            'scgs_max_price': max_price,
            'scgs_discount': discount,
            'scgs_dispatch': dispatch,
            'scgs_shipping': shipping,
            'scgs_currency': currency,
            'scgs_attribute': attribute,
            'scgs_version_urls': version_urls,
            'scgs_review_count': review_count,
            'scgs_grade_count': grade_count,
            'scgs_sales_total': sales_total,
            'scgs_total_inventory': total_inventory,
            'scgs_favornum': favornum,
            'scgs_image_url': main_image_url,
            'scgs_extra_image_urls': extra_image_urls,
            'scgs_description': description,
            'scgs_category': category,
            'scgs_category_url': category_url,
            'scgs_tags': tags,
            'scgs_shop_name': shop_name,
            'scgs_shop_url': shop_url,
            'scgs_generation_time': generation_time,
            'scgs_platform': platform,
            'scgs_platform_url': platform_url,
            'scgs_crawl_time': crawl_time,
            'scgs_create_time': create_time,
            'scgs_status': status,
            'scgs_questions': questions,
            'scgs_is_delete': is_delete,
            'scgs_reserve_field_1': reserve_field_1,
            'scgs_reserve_field_2': reserve_field_2,
            'scgs_reserve_field_3': reserve_field_3,
            'scgs_reserve_field_4': reserve_field_4,
            'scgs_reserve_field_5': reserve_field_5,
            'scgs_reserve_field_6': reserve_field_6,
            'scgs_reserve_field_7': reserve_field_7,
        }

    data_mp = {"table": table_name, "data": sku_mp}
    push_data_into_redis(rds, conf, data_mp)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def parse_comment(rds, conf, mp, html):
    mapping = eval(mp)
    page_url = mapping['page_url']
    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]
    sites = {'com': 'US', 'co.uk': 'UK', 'fr': 'FR', 'de': 'DE', 'es': 'ES', 'ca': 'CA', 'it': 'IT',
             'in': 'IN', 'co.jp': 'JP', 'com.au': 'AU', 'com.mx': 'MX'}
    asin = mapping['asin']

    comment = Comment(html, suffix)

    if comment.is_first_page():
        latest_comment_date = comment.get_latest_comment_date()
        if latest_comment_date:
            if latest_comment_date != '1900-01-01':
                hash_key = '{}{}'.format(asin, sites[suffix])
                rds.set_hash(conf.REDIS_REVIEW_DATE, {hash_key: latest_comment_date})
            else:
                collect_error(rds, conf, mp, error='latest_comment_date_1900')
                print('latest_comment_date error')
                return

        grade_score = comment.get_score()
        grade_num = comment.get_count()

        grade_mp = {
            'rc_listing_id': mapping['listing_id'],
            'rc_product_id': asin,
            'rc_product_url': "https://www.amazon.{}/dp/{}".format(suffix, asin),
            'rc_platform': 'amazon',
            'rc_site': sites[suffix],
            'rc_grade_overall': grade_score,
            'rc_grade_1_count': 0,
            'rc_grade_2_count': 0,
            'rc_grade_3_count': 0,
            'rc_grade_4_count': 0,
            'rc_grade_5_count': 0,
            'rc_reviews_count': grade_num,
            'rc_reviews_url': '',
            'is_delete': 0,
            'rc_reserve_1': '',
            'rc_reserve_2': '',
        }
        data_mp = {"table": conf.MYSQL_TABLE_GRADE, "data": grade_mp}
        push_data_into_redis(rds, conf, data_mp)

    comments_list = comment.get_comment_list()
    for xp in comments_list:
        date_limit = mapping.get('date', '')
        review_date = comment.get_comment_date(xp)
        if not date_limit or datetime.strptime(review_date, '%Y-%m-%d') > datetime.strptime(date_limit, '%Y-%m-%d'):
            review_id = comment.get_comment_id(xp)
            review_grade = comment.get_comment_grade(xp)
            review_title = comment.get_comment_title(xp)
            review_user = comment.get_comment_user(xp)
            review_user_link = comment.get_comment_user_link(xp)
            review_user_id_xp = re.findall(r'account.([A-Z-0-9]+)/', review_user_link)
            review_user_id = ''
            if review_user_id_xp:
                review_user_id = review_user_id_xp[0]
            review_content = comment.get_comment_content(xp)
            review_image = comment.get_comment_image(xp)
            review_vote = comment.get_comment_vote(xp)
            review_verified = comment.get_comment_verified(xp)
            review_mp = {
                'rc_listing_id': mapping['listing_id'],
                'rc_product_id': asin,
                'rc_product_url': "https://www.amazon.{}/dp/{}".format(suffix, asin),
                'rc_platform': 'amazon',
                'rc_site': sites[suffix],
                'rc_review_id': review_id,
                'rc_review_time': review_date,
                'rc_customer': review_user,
                'rc_customer_email': '',
                'rc_review_title': review_title,
                'rc_review_content': review_content,
                'rc_review_image': review_image,
                'rc_review_grade': review_grade,
                'rc_review_grade_detail': '',
                'is_delete': 0,
                'rc_reserve_1': review_vote,
                'rc_reserve_2': review_verified,
                'rc_reserve_3': review_user_id,
            }
            data_mp = {"table": conf.MYSQL_TABLE_REVIEW, "data": review_mp}
            push_data_into_redis(rds, conf, data_mp)
        else:
            print('over date')
            break
    else:
        next_page = comment.get_next_page()
        if next_page:
            mapping['page_url'] = next_page
            rds.rds.lpush(conf.REDIS_START_URLS, mapping)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def parse_comment_first(rds, conf, mp, html):
    mapping = eval(mp)
    page_url = mapping['page_url']
    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]
    sites = {'com': 'US', 'co.uk': 'UK', 'fr': 'FR', 'de': 'DE', 'es': 'ES', 'ca': 'CA', 'it': 'IT',
             'in': 'IN', 'co.jp': 'JP', 'com.au': 'AU', 'com.mx': 'MX'}
    asin = mapping['asin']

    comment = Comment(html, suffix)

    if comment.is_first_page():
        total_page = comment.get_page_num()
        for i in range(2, int(total_page)+1):
            new_comment_url = "https://www.amazon.{site}/product-reviews/{asin}/?&pageNumber={page}" \
                          "&pageSize=50&sortBy=recent".format(site=suffix, page=i, asin=asin)
            mapping['page_url'] = new_comment_url
            rds.rds.lpush(conf.REDIS_START_URLS, mapping)

        latest_comment_date = comment.get_latest_comment_date()
        if latest_comment_date:
            if latest_comment_date != '1900-01-01':
                hash_key = '{}{}'.format(asin, sites[suffix])
                rds.set_hash(conf.REDIS_REVIEW_DATE, {hash_key: latest_comment_date})
            else:
                collect_error(rds, conf, mp, error='latest_comment_date_1900')
                print('latest_comment_date error')
                return

        grade_score = comment.get_score()
        grade_num = comment.get_count()

        grade_mp = {
            'rc_listing_id': mapping['listing_id'],
            'rc_product_id': asin,
            'rc_product_url': "https://www.amazon.{}/dp/{}".format(suffix, asin),
            'rc_platform': 'amazon',
            'rc_site': sites[suffix],
            'rc_grade_overall': grade_score,
            'rc_grade_1_count': 0,
            'rc_grade_2_count': 0,
            'rc_grade_3_count': 0,
            'rc_grade_4_count': 0,
            'rc_grade_5_count': 0,
            'rc_reviews_count': grade_num,
            'rc_reviews_url': '',
            'is_delete': 0,
            'rc_reserve_1': '',
            'rc_reserve_2': '',
        }
        data_mp = {"table": conf.MYSQL_TABLE_GRADE, "data": grade_mp}
        push_data_into_redis(rds, conf, data_mp)

    comments_list = comment.get_comment_list()
    for xp in comments_list:
        date_limit = mapping.get('date', '')
        review_date = comment.get_comment_date(xp)
        if not date_limit or datetime.strptime(review_date, '%Y-%m-%d') > datetime.strptime(date_limit, '%Y-%m-%d'):
            review_id = comment.get_comment_id(xp)
            review_grade = comment.get_comment_grade(xp)
            review_title = comment.get_comment_title(xp)
            review_user = comment.get_comment_user(xp)
            review_user_link = comment.get_comment_user_link(xp)
            review_user_id_xp = re.findall(r'account.([A-Z-0-9]+)/', review_user_link)
            review_user_id = ''
            if review_user_id_xp:
                review_user_id = review_user_id_xp[0]
            review_content = comment.get_comment_content(xp)
            review_image = comment.get_comment_image(xp)
            review_vote = comment.get_comment_vote(xp)
            review_verified = comment.get_comment_verified(xp)
            review_mp = {
                'rc_listing_id': mapping['listing_id'],
                'rc_product_id': asin,
                'rc_product_url': "https://www.amazon.{}/dp/{}".format(suffix, asin),
                'rc_platform': 'amazon',
                'rc_site': sites[suffix],
                'rc_review_id': review_id,
                'rc_review_time': review_date,
                'rc_customer': review_user,
                'rc_customer_email': '',
                'rc_review_title': review_title,
                'rc_review_content': review_content,
                'rc_review_image': review_image,
                'rc_review_grade': review_grade,
                'rc_review_grade_detail': '',
                'is_delete': 0,
                'rc_reserve_1': review_vote,
                'rc_reserve_2': review_verified,
                'rc_reserve_3': review_user_id,
            }
            data_mp = {"table": conf.MYSQL_TABLE_REVIEW, "data": review_mp}
            push_data_into_redis(rds, conf, data_mp)
        else:
            print('over date')
            break
    else:
        next_page = comment.get_next_page()
        if next_page:
            mapping['page_url'] = next_page
            rds.rds.lpush(conf.REDIS_START_URLS, mapping)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def parse_cate(rds, conf, mp, html):
    mapping = eval(mp)
    page_url = mapping['page_url']
    cate_entry = mapping['cate_entry']
    suffix = re.findall(r'www.amazon.(.*?)/', page_url)[0]

    sel = etree.HTML(html)
    parents = sel.xpath('//li[@class="zg_browseUp"]/a/text()')
    select = sel.xpath('//li/span[@class="zg_selected"]/text()')
    select_parent = sel.xpath('//li/span[@class="zg_selected"]/../../../li/a/text()')
    cate_lst = parents[1:]
    if select_parent and parents[-1].strip() == select_parent[0].strip():
        cate_lst.extend(select)
    else:
        cate_lst.extend(select_parent)
        cate_lst.extend(select)
    cate = '>'.join([item.strip() for item in cate_lst])
    if cate:
        unique_cate = '{}{}{}'.format(cate, cate_entry, suffix)
        if not rds.is_member("unique_cate", unique_cate):
            rank = cate.count('>') + 1
            cate_mp = {
                'category': cate,
                'url': page_url,
                'entry': cate_entry,
                'rank': rank
            }
            data_mp = {"table": conf.MYSQL_TABLE_TOP_CATE, "data": cate_mp}
            push_data_into_redis(rds, conf, data_mp)
            rds.add_set("unique_cate", unique_cate)
    else:
        print('None')
    children = sel.xpath('//ul[@id="zg_browseRoot"]//li/span[@class="zg_selected"]/../../ul/li/a')
    for child in children:
        child_url = child.xpath('./@href')[0].strip()
        mapping['page_url'] = child_url
        rds.rds.rpush(conf.REDIS_START_URLS, mapping)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def collect_error(rds, conf, mp, **kwargs):
    mapping = eval(mp)
    mapping["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    mapping.update(kwargs)
    rds.add_set(conf.REDIS_ERROR_URLS, mapping)
    rds.remove_member(conf.REDIS_CRAWL_URLS, mp)


def push_data_into_redis(rds, conf, data_mp):
    data_json = json.dumps(data_mp)
    rds.rds.lpush(conf.REDIS_DATA_LIST, data_json)




